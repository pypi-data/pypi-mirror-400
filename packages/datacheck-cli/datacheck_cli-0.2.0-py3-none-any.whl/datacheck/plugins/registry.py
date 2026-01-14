"""Registry for custom validation rules."""

from collections.abc import Callable
from typing import Any

import pandas as pd

from datacheck.exceptions import RuleDefinitionError


class RuleRegistry:
    """Registry for storing and retrieving custom validation rules.

    The registry maintains a mapping of rule names to their implementations,
    allowing custom rules to be loaded and executed dynamically.

    Example:
        >>> registry = RuleRegistry()
        >>> registry.register("my_rule", my_rule_func)
        >>> rule_func = registry.get("my_rule")
    """

    def __init__(self) -> None:
        """Initialize empty rule registry."""
        self._rules: dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """Register a custom rule.

        Args:
            name: Name of the rule
            func: Rule function

        Raises:
            RuleDefinitionError: If rule name is already registered
        """
        if name in self._rules:
            raise RuleDefinitionError(f"Rule '{name}' is already registered")

        self._rules[name] = func

    def get(self, name: str) -> Callable | None:
        """Get a registered rule by name.

        Args:
            name: Name of the rule

        Returns:
            Rule function or None if not found
        """
        return self._rules.get(name)

    def has_rule(self, name: str) -> bool:
        """Check if a rule is registered.

        Args:
            name: Name of the rule

        Returns:
            True if rule exists
        """
        return name in self._rules

    def list_rules(self) -> list[str]:
        """List all registered rule names.

        Returns:
            List of rule names
        """
        return list(self._rules.keys())

    def clear(self) -> None:
        """Clear all registered rules."""
        self._rules.clear()

    def execute_rule(
        self,
        rule_name: str,
        column: pd.Series,
        params: dict[str, Any] | None = None
    ) -> pd.Series:
        """Execute a custom rule.

        Args:
            rule_name: Name of the rule to execute
            column: Column data to validate
            params: Optional parameters for the rule

        Returns:
            Boolean series indicating valid rows

        Raises:
            RuleDefinitionError: If rule not found or execution fails
        """
        rule_func = self.get(rule_name)

        if rule_func is None:
            raise RuleDefinitionError(f"Custom rule '{rule_name}' not found in registry")

        try:
            if params:
                return rule_func(column, **params)  # type: ignore[no-any-return]
            else:
                return rule_func(column)  # type: ignore[no-any-return]
        except Exception as e:
            raise RuleDefinitionError(f"Error executing custom rule '{rule_name}': {e}") from e


# Global registry instance
_global_registry = RuleRegistry()


def get_global_registry() -> RuleRegistry:
    """Get the global rule registry.

    Returns:
        Global RuleRegistry instance
    """
    return _global_registry
