"""Custom rule plugin system for DataCheck."""

from datacheck.plugins.decorators import custom_rule, validate_custom_rule_signature
from datacheck.plugins.loader import PluginLoader
from datacheck.plugins.registry import RuleRegistry, get_global_registry

__all__ = [
    "custom_rule",
    "validate_custom_rule_signature",
    "RuleRegistry",
    "get_global_registry",
    "PluginLoader",
]
