"""Configuration parsing and validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from datacheck.exceptions import ConfigurationError


@dataclass
class RuleConfig:
    """Configuration for a single validation rule.

    Attributes:
        name: Unique name for this rule
        column: Name of the column to validate
        rules: Dictionary of rule types and their parameters
    """

    name: str
    column: str
    rules: dict[str, Any]

    def __post_init__(self) -> None:
        """Validate rule configuration after initialization."""
        if not self.name:
            raise ConfigurationError("Rule name cannot be empty")
        if not self.column:
            raise ConfigurationError(f"Column name cannot be empty for rule '{self.name}'")
        if not self.rules:
            raise ConfigurationError(f"Rules cannot be empty for rule '{self.name}'")

        # Validate rule types
        valid_rule_types = {"not_null", "min", "max", "unique", "regex", "allowed_values", "custom"}
        invalid_rules = set(self.rules.keys()) - valid_rule_types
        if invalid_rules:
            raise ConfigurationError(
                f"Invalid rule types in '{self.name}': {', '.join(invalid_rules)}. "
                f"Valid types: {', '.join(sorted(valid_rule_types))}"
            )


@dataclass
class SamplingConfig:
    """Configuration for data sampling."""

    method: str = "none"  # none, random, stratified, top, systematic
    rate: float | None = None  # For random sampling
    count: int | None = None  # For random/stratified/top
    stratify_by: str | None = None  # For stratified sampling
    seed: int | None = None  # For reproducibility

    def __post_init__(self) -> None:
        """Validate sampling configuration."""
        valid_methods = ["none", "random", "stratified", "top", "systematic"]
        if self.method not in valid_methods:
            raise ConfigurationError(
                f"Invalid sampling method '{self.method}'. "
                f"Must be one of: {', '.join(valid_methods)}"
            )

        if self.method == "random":
            if self.rate is None and self.count is None:
                raise ConfigurationError(
                    "Random sampling requires either 'rate' or 'count'"
                )

        if self.method == "stratified":
            if self.stratify_by is None:
                raise ConfigurationError(
                    "Stratified sampling requires 'stratify_by' column"
                )
            if self.count is None:
                raise ConfigurationError(
                    "Stratified sampling requires 'count'"
                )

        if self.method == "top":
            if self.count is None:
                raise ConfigurationError("Top-N sampling requires 'count'")


@dataclass
class ValidationConfig:
    """Complete validation configuration.

    Attributes:
        checks: List of rule configurations
        plugins: List of plugin file paths
        sampling: Optional sampling configuration
    """

    checks: list[RuleConfig]
    plugins: list[str] | None = None
    sampling: SamplingConfig | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.checks:
            raise ConfigurationError("Configuration must contain at least one check")

        # Check for duplicate rule names
        names = [check.name for check in self.checks]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            raise ConfigurationError(
                f"Duplicate rule names found: {', '.join(set(duplicates))}"
            )

        # Initialize plugins list if None
        if self.plugins is None:
            self.plugins = []


class ConfigLoader:
    """Loader for YAML configuration files."""

    @staticmethod
    def load(config_path: str | Path) -> ValidationConfig:
        """Load and parse a YAML configuration file.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            ValidationConfig object

        Raises:
            ConfigurationError: If file not found, invalid YAML, or invalid schema
        """
        path = Path(config_path)

        # Check if file exists
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        if not path.is_file():
            raise ConfigurationError(f"Configuration path is not a file: {config_path}")

        # Read and parse YAML
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {config_path}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Error reading {config_path}: {e}") from e

        # Validate schema
        if data is None:
            raise ConfigurationError(f"Configuration file is empty: {config_path}")

        if not isinstance(data, dict):
            raise ConfigurationError(
                f"Configuration must be a dictionary, got {type(data).__name__}"
            )

        if "checks" not in data:
            raise ConfigurationError("Configuration must contain 'checks' key")

        if not isinstance(data["checks"], list):
            raise ConfigurationError(
                f"'checks' must be a list, got {type(data['checks']).__name__}"
            )

        # Parse checks
        checks = []
        for idx, check_data in enumerate(data["checks"]):
            if not isinstance(check_data, dict):
                raise ConfigurationError(
                    f"Check at index {idx} must be a dictionary, "
                    f"got {type(check_data).__name__}"
                )

            # Validate required fields
            if "name" not in check_data:
                raise ConfigurationError(f"Check at index {idx} missing 'name' field")
            if "column" not in check_data:
                raise ConfigurationError(
                    f"Check '{check_data.get('name', idx)}' missing 'column' field"
                )
            if "rules" not in check_data:
                raise ConfigurationError(
                    f"Check '{check_data['name']}' missing 'rules' field"
                )

            try:
                rule_config = RuleConfig(
                    name=check_data["name"],
                    column=check_data["column"],
                    rules=check_data["rules"],
                )
                checks.append(rule_config)
            except ConfigurationError:
                raise
            except Exception as e:
                raise ConfigurationError(
                    f"Error parsing check '{check_data.get('name', idx)}': {e}"
                ) from e

        # Parse plugins (optional)
        plugins = data.get("plugins", [])
        if not isinstance(plugins, list):
            raise ConfigurationError("'plugins' must be a list of file paths")

        # Parse sampling (optional)
        sampling = None
        if "sampling" in data:
            sampling_data = data["sampling"]
            if not isinstance(sampling_data, dict):
                raise ConfigurationError("'sampling' must be a dictionary")

            try:
                sampling = SamplingConfig(
                    method=sampling_data.get("method", "none"),
                    rate=sampling_data.get("rate"),
                    count=sampling_data.get("count"),
                    stratify_by=sampling_data.get("stratify_by"),
                    seed=sampling_data.get("seed")
                )
            except ConfigurationError:
                raise
            except Exception as e:
                raise ConfigurationError(f"Error parsing sampling config: {e}") from e

        return ValidationConfig(checks=checks, plugins=plugins, sampling=sampling)

    @staticmethod
    def find_config() -> Path | None:
        """Find configuration file in common locations.

        Searches for configuration files in the following order:
        1. .datacheck.yaml
        2. .datacheck.yml
        3. datacheck.yaml
        4. datacheck.yml

        Returns:
            Path to configuration file if found, None otherwise
        """
        search_names = [
            ".datacheck.yaml",
            ".datacheck.yml",
            "datacheck.yaml",
            "datacheck.yml",
        ]

        for name in search_names:
            path = Path(name)
            if path.exists() and path.is_file():
                return path

        return None


__all__ = [
    "RuleConfig",
    "SamplingConfig",
    "ValidationConfig",
    "ConfigLoader",
]
