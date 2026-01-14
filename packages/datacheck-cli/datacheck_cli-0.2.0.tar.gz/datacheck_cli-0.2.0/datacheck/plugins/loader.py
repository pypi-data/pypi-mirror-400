"""Plugin loader for custom validation rules."""

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from datacheck.exceptions import ConfigurationError
from datacheck.plugins.registry import get_global_registry


class PluginLoader:
    """Loads custom validation rules from Python files.

    The loader scans Python files for functions decorated with @custom_rule
    and registers them in the global rule registry.

    Example:
        >>> loader = PluginLoader()
        >>> loader.load_from_file("my_rules.py")
        >>> # Rules from my_rules.py are now available
    """

    def __init__(self) -> None:
        """Initialize plugin loader."""
        self.registry = get_global_registry()
        self._loaded_modules: list[str] = []

    def load_from_file(self, file_path: str) -> list[str]:
        """Load custom rules from a Python file.

        Args:
            file_path: Path to Python file containing custom rules

        Returns:
            List of rule names that were loaded

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        path = Path(file_path)

        if not path.exists():
            raise ConfigurationError(f"Plugin file not found: {file_path}")

        if not path.suffix == ".py":
            raise ConfigurationError(f"Plugin file must be a Python file: {file_path}")

        try:
            # Load module from file
            module_name = f"datacheck_plugin_{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)

            if spec is None or spec.loader is None:
                raise ConfigurationError(f"Failed to load plugin: {file_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find and register custom rules
            loaded_rules = self._register_rules_from_module(module)
            self._loaded_modules.append(module_name)

            return loaded_rules

        except Exception as e:
            raise ConfigurationError(f"Error loading plugin {file_path}: {e}") from e

    def _register_rules_from_module(self, module: Any) -> list[str]:
        """Register all custom rules from a module.

        Args:
            module: Python module to scan for rules

        Returns:
            List of registered rule names
        """
        loaded_rules = []

        for name, obj in inspect.getmembers(module):
            if callable(obj) and hasattr(obj, "_is_custom_rule"):
                rule_name = getattr(obj, "_rule_name", name)

                # Register rule if not already registered
                if not self.registry.has_rule(rule_name):
                    self.registry.register(rule_name, obj)
                    loaded_rules.append(rule_name)

        return loaded_rules

    def load_from_directory(self, directory_path: str) -> list[str]:
        """Load all custom rules from a directory.

        Args:
            directory_path: Path to directory containing Python files

        Returns:
            List of all loaded rule names

        Raises:
            ConfigurationError: If directory cannot be accessed
        """
        dir_path = Path(directory_path)

        if not dir_path.exists():
            raise ConfigurationError(f"Plugin directory not found: {directory_path}")

        if not dir_path.is_dir():
            raise ConfigurationError(f"Path is not a directory: {directory_path}")

        all_loaded_rules = []

        # Load all .py files in directory
        for py_file in dir_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue  # Skip private files

            loaded_rules = self.load_from_file(str(py_file))
            all_loaded_rules.extend(loaded_rules)

        return all_loaded_rules
