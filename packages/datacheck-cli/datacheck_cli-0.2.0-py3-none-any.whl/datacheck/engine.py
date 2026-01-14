"""Validation engine orchestration."""

from pathlib import Path
from typing import Any

import pandas as pd

from datacheck.config import ConfigLoader, ValidationConfig
from datacheck.exceptions import ConfigurationError, DataLoadError, ValidationError
from datacheck.loader import LoaderFactory
from datacheck.results import RuleResult, ValidationSummary
from datacheck.rules import RuleFactory
from datacheck.sampling import DataSampler


class ValidationEngine:
    """Engine for orchestrating data validation.

    The ValidationEngine coordinates the entire validation process:
    1. Loads data from various sources (CSV, Parquet, databases)
    2. Loads and parses validation configuration
    3. Creates rule instances from configuration
    4. Executes all rules against the data
    5. Aggregates results into a summary
    """

    def __init__(
        self,
        config: ValidationConfig | None = None,
        config_path: str | Path | None = None,
        parallel: bool = False,
        workers: int | None = None,
        notifier: Any = None,
    ) -> None:
        """Initialize validation engine.

        Args:
            config: Pre-loaded validation configuration (optional)
            config_path: Path to configuration file (optional)
            parallel: Enable parallel execution (default: False)
            workers: Number of worker processes (default: CPU count)
            notifier: Optional notifier instance (e.g., SlackNotifier) to send results

        Raises:
            ConfigurationError: If neither config nor config_path provided, or both provided
        """
        if config is not None and config_path is not None:
            raise ConfigurationError("Cannot provide both config and config_path")

        if config is None and config_path is None:
            # Try to auto-discover config file
            found_config = ConfigLoader.find_config()
            if found_config is None:
                raise ConfigurationError(
                    "No configuration provided and no config file found. "
                    "Searched for: .datacheck.yaml, .datacheck.yml, datacheck.yaml, datacheck.yml"
                )
            config_path = found_config

        if config_path is not None:
            self.config = ConfigLoader.load(config_path)
        else:
            self.config = config  # type: ignore

        # Store parallel execution settings
        self.parallel = parallel
        self.workers = workers

        # Store notifier for sending results
        self.notifier = notifier

        # Load plugins if specified
        if self.config.plugins:
            from datacheck.plugins.loader import PluginLoader

            loader = PluginLoader()

            for plugin_path in self.config.plugins:
                try:
                    loader.load_from_file(plugin_path)
                except Exception as e:
                    raise ConfigurationError(f"Failed to load plugin {plugin_path}: {e}") from e

    def validate_file(
        self,
        file_path: str | Path,
        **loader_kwargs: Any,
    ) -> ValidationSummary:
        """Validate a data file against configured rules.

        Args:
            file_path: Path to the data file to validate
            **loader_kwargs: Additional arguments passed to the data loader
                            May include sampling parameters:
                            - sample_rate: Random sample rate (0.0 to 1.0)
                            - sample_count: Number of rows to sample
                            - top: Validate only first N rows
                            - stratify: Column name for stratified sampling
                            - seed: Random seed for reproducibility

        Returns:
            ValidationSummary with aggregated results

        Raises:
            DataLoadError: If data cannot be loaded
            ValidationError: If validation fails unexpectedly
        """
        # Extract sampling parameters from loader_kwargs
        sample_rate = loader_kwargs.pop("sample_rate", None)
        sample_count = loader_kwargs.pop("sample_count", None)
        top = loader_kwargs.pop("top", None)
        stratify = loader_kwargs.pop("stratify", None)
        seed = loader_kwargs.pop("seed", None)

        # Load data
        try:
            df = LoaderFactory.load(file_path, **loader_kwargs)
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading data: {e}") from e

        # Apply sampling (CLI arguments override config)
        df = self._apply_sampling(
            df,
            sample_rate=sample_rate,
            sample_count=sample_count,
            top=top,
            stratify=stratify,
            seed=seed
        )

        # Validate the loaded data
        summary = self.validate_dataframe(df)

        # Send notification if notifier configured
        if self.notifier:
            try:
                self.notifier.send_summary(summary)
            except Exception as e:
                # Log error but don't fail validation
                import warnings
                warnings.warn(f"Failed to send notification: {e}", RuntimeWarning, stacklevel=2)

        return summary

    def validate_dataframe(self, df: pd.DataFrame) -> ValidationSummary:
        """Validate a DataFrame against configured rules.

        Args:
            df: DataFrame to validate

        Returns:
            ValidationSummary with aggregated results

        Raises:
            ValidationError: If validation fails unexpectedly
        """
        # Collect all rules first
        all_rules = []
        for check_config in self.config.checks:
            try:
                rules = RuleFactory.create_rules(check_config)
                all_rules.extend(rules)
            except Exception as e:
                # If rule creation fails, create error result directly
                error_result = RuleResult(
                    rule_name=check_config.name,
                    column=check_config.column,
                    passed=False,
                    total_rows=len(df),
                    error=f"Error creating rules: {e}",
                )
                # Return early with error if rule creation fails
                return ValidationSummary(results=[error_result])

        # Execute rules (parallel or sequential)
        if self.parallel and len(df) > 10000:  # Use parallel for large datasets
            from datacheck.parallel import ParallelExecutor

            executor = ParallelExecutor(workers=self.workers)
            results = executor.validate_parallel(df, all_rules)
        else:
            # Sequential execution
            results = []
            for rule in all_rules:
                try:
                    result = rule.validate(df)
                    results.append(result)
                except Exception as e:
                    error_result = RuleResult(
                        rule_name=rule.name,
                        column=rule.column,
                        passed=False,
                        total_rows=len(df),
                        error=f"Unexpected error executing rule: {e}",
                    )
                    results.append(error_result)

        return ValidationSummary(results=results)

    def validate(
        self,
        file_path: str | Path | None = None,
        df: pd.DataFrame | None = None,
        **loader_kwargs: Any,
    ) -> ValidationSummary:
        """Validate data from either a file or DataFrame.

        Args:
            file_path: Path to the data file (optional)
            df: DataFrame to validate (optional)
            **loader_kwargs: Additional arguments passed to the data loader

        Returns:
            ValidationSummary with aggregated results

        Raises:
            ValidationError: If neither file_path nor df provided, or both provided
            DataLoadError: If data cannot be loaded from file
        """
        if file_path is not None and df is not None:
            raise ValidationError("Cannot provide both file_path and df")

        if file_path is None and df is None:
            raise ValidationError("Must provide either file_path or df")

        if file_path is not None:
            return self.validate_file(file_path, **loader_kwargs)
        else:
            return self.validate_dataframe(df)  # type: ignore

    def _apply_sampling(
        self,
        df: pd.DataFrame,
        sample_rate: float | None = None,
        sample_count: int | None = None,
        top: int | None = None,
        stratify: str | None = None,
        seed: int | None = None,
    ) -> pd.DataFrame:
        """Apply sampling to DataFrame.

        CLI arguments take precedence over config file settings.

        Args:
            df: DataFrame to sample
            sample_rate: Random sample rate (CLI argument)
            sample_count: Number of rows to sample (CLI argument)
            top: First N rows (CLI argument)
            stratify: Column for stratified sampling (CLI argument)
            seed: Random seed (CLI argument)

        Returns:
            Sampled DataFrame (or original if no sampling configured)

        Raises:
            DataLoadError: If sampling configuration is invalid
        """
        # Check if any CLI sampling arguments provided
        has_cli_sampling = any([
            sample_rate is not None,
            sample_count is not None,
            top is not None,
            stratify is not None,
        ])

        # If CLI arguments provided, use them (override config)
        if has_cli_sampling:
            # Top-N sampling
            if top is not None:
                return DataSampler.top_n(df, top)

            # Stratified sampling
            if stratify is not None:
                if sample_count is None:
                    raise DataLoadError("--stratify requires --sample-count")
                return DataSampler.stratified_sample(df, stratify, sample_count, seed=seed)

            # Random sampling
            if sample_rate is not None or sample_count is not None:
                return DataSampler.random_sample(df, rate=sample_rate, count=sample_count, seed=seed)

        # Otherwise, use config file sampling
        return self._apply_config_sampling(df)

    def _apply_config_sampling(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply sampling from config file.

        Args:
            df: DataFrame to sample

        Returns:
            Sampled DataFrame (or original if no sampling configured)

        Raises:
            DataLoadError: If sampling configuration is invalid
        """
        if self.config.sampling is None:
            return df

        sampling_config = self.config.sampling

        # No sampling
        if sampling_config.method == "none":
            return df

        # Top-N sampling
        if sampling_config.method == "top":
            if sampling_config.count is None:
                raise DataLoadError("Top-N sampling requires 'count' in config")
            return DataSampler.top_n(df, sampling_config.count)

        # Stratified sampling
        if sampling_config.method == "stratified":
            if sampling_config.stratify_by is None:
                raise DataLoadError("Stratified sampling requires 'stratify_by' in config")
            if sampling_config.count is None:
                raise DataLoadError("Stratified sampling requires 'count' in config")
            return DataSampler.stratified_sample(
                df,
                sampling_config.stratify_by,
                sampling_config.count,
                seed=sampling_config.seed
            )

        # Random sampling
        if sampling_config.method == "random":
            return DataSampler.random_sample(
                df,
                rate=sampling_config.rate,
                count=sampling_config.count,
                seed=sampling_config.seed
            )

        # Systematic sampling
        if sampling_config.method == "systematic":
            # For systematic sampling, we need an interval
            # Calculate from rate if provided, otherwise use a default
            if sampling_config.rate is not None:
                interval = int(1.0 / sampling_config.rate)
            else:
                # Default to every 10th row
                interval = 10
            return DataSampler.systematic_sample(df, interval=interval)

        return df


__all__ = [
    "ValidationEngine",
]
