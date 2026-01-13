"""
Utility functions for database context managers and decorators.

This module provides common utilities for working with database sessions,
function inspection, and type detection.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Union, get_args, get_origin

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


def is_async_function(func: Callable[..., Any]) -> bool:
    """
    Check if a function is async.

    Args:
        func: The function to check

    Returns:
        True if the function is async, False otherwise
    """
    return inspect.iscoroutinefunction(func)


def find_session_param_by_type(
    func: Callable[..., Any], session_type: type[Session] | type[AsyncSession]
) -> str | None:
    """
    Find the parameter name that has the specified session type annotation.

    Args:
        func: The function to inspect
        session_type: The session type to look for (Session or AsyncSession)

    Returns:
        Parameter name if found, None otherwise
    """
    sig = inspect.signature(func)
    for param_name, param in sig.parameters.items():
        # Check if the parameter has a type annotation
        if param.annotation == inspect.Parameter.empty:
            continue

        annotation = param.annotation

        # Handle string annotations (forward references)
        if isinstance(annotation, str):
            # Try to resolve the annotation
            # For now, we'll skip string annotations and rely on runtime type checking
            continue

        # Direct type match
        if annotation is session_type:
            return param_name

        # Check if it's a subclass (for inheritance)
        try:
            if isinstance(annotation, type) and issubclass(annotation, session_type):
                return param_name
        except TypeError:
            # annotation might not be a class
            pass

        # Handle generic types (Union, Optional, etc.)
        origin = get_origin(annotation)
        if origin is not None:
            args = get_args(annotation)
            # Check if session_type is in the type arguments
            for arg in args:
                if arg is session_type:
                    return param_name
                # Check for subclasses in args
                try:
                    if isinstance(arg, type) and issubclass(arg, session_type):
                        return param_name
                except TypeError:
                    pass

    return None


def find_session_in_args(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    func: Callable[..., Any],
    session_param: str | None,
    session_type: type[Session] | type[AsyncSession],
) -> Union[Session, AsyncSession, None]:
    """
    Find a database session in function arguments.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments
        func: The function being decorated
        session_param: Optional name of the session parameter
        session_type: The expected session type (Session or AsyncSession)

    Returns:
        Session or AsyncSession if found, None otherwise
    """
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    # If session_param is specified, check only that parameter
    if session_param is not None:
        # Check if it's in kwargs
        if session_param in kwargs:
            arg = kwargs[session_param]
            if isinstance(arg, session_type):
                return arg

        # Check if it's in positional args
        if session_param in param_names:
            param_index = param_names.index(session_param)
            if param_index < len(args):
                arg = args[param_index]
                if isinstance(arg, session_type):
                    return arg

        return None

    # Auto-detect: check positional arguments
    for i, arg in enumerate(args):
        if i < len(param_names):
            if isinstance(arg, session_type):
                return arg

    # Auto-detect: check keyword arguments
    for param_name, param in sig.parameters.items():
        if param_name in kwargs:
            arg = kwargs[param_name]
            if isinstance(arg, session_type):
                return arg

    return None
