"""Reflection utilities for inspecting objects at runtime."""

from typing import Any


def get_class_name(object: Any) -> str:
    """Get the class name of an object.

    This utility function provides a consistent way to retrieve the class name
    of an object instance, which is useful for logging, error messages, and debugging.

    Args:
        instance: The object instance to get the class name from.

    Returns:
        The name of the instance's class as a string.

    Example:
        >>> class MyClass:
        ...     pass
        >>> obj = MyClass()
        >>> get_class_name(obj)
        'MyClass'
    """
    return type(object).__name__
