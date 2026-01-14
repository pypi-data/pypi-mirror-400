"""Decorators for custom validation rules."""

import functools
from collections.abc import Callable
from typing import Any


def custom_rule(func: Callable) -> Callable:
    """Decorator to mark a function as a custom validation rule.

    Custom rules must accept a pandas Series as the first parameter and return
    a pandas Series of boolean values (True = valid, False = invalid).

    Example:
        >>> @custom_rule
        ... def is_business_email(column: pd.Series, allowed_domains: list) -> pd.Series:
        ...     return column.str.endswith(tuple(allowed_domains))

        >>> # Use in config
        >>> checks:
        ...   - name: email_check
        ...     column: email
        ...     rules:
        ...       custom:
        ...         rule: is_business_email
        ...         params:
        ...           allowed_domains: ["company.com"]

    Args:
        func: Function to be marked as a custom rule

    Returns:
        Decorated function with metadata
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    # Mark function as custom rule
    wrapper._is_custom_rule = True  # type: ignore
    wrapper._rule_name = func.__name__  # type: ignore
    wrapper._original_func = func  # type: ignore

    return wrapper


def validate_custom_rule_signature(func: Callable) -> bool:
    """Validate that a custom rule has the correct signature.

    Custom rules must:
    - Accept a pandas Series as first parameter
    - Return a pandas Series of booleans
    - Accept **kwargs for additional parameters

    Args:
        func: Function to validate

    Returns:
        True if signature is valid

    Raises:
        ValueError: If signature is invalid
    """
    import inspect

    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if len(params) < 1:
        raise ValueError(
            f"Custom rule '{func.__name__}' must accept at least one parameter (column)"
        )

    # First parameter should be the column (Series)
    first_param = params[0]
    if first_param.annotation != inspect.Parameter.empty:
        import pandas as pd
        if first_param.annotation != pd.Series:
            raise ValueError(
                f"Custom rule '{func.__name__}' first parameter should be pd.Series"
            )

    return True
