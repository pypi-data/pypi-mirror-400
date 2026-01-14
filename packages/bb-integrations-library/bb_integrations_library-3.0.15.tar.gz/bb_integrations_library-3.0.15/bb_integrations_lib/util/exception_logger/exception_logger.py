import functools
import traceback
from typing import Dict, Any, Callable, Optional
import json
from datetime import datetime


class ExceptionLogger:
    """
    A class that provides a decorator for catching and logging exceptions.
    """

    def __init__(self):
        """Initialize a new exception logger with an empty log."""
        self._exception_log: Dict[str, Any] = {}

    def catch_exceptions(self, identifier_param: Optional[str] = None):
        """
        Decorator that catches exceptions and logs them to this logger's dictionary.

        Args:
            identifier_param (str, optional): The parameter name to use as the identifier in the log.
                                             If None, will use function name + args as identifier.
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Determine the identifier
                identifier = self._get_identifier(func, args, kwargs, identifier_param)

                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Log the exception
                    self._exception_log[identifier] = {
                        'timestamp': datetime.now().isoformat(),
                        'exception_type': type(e).__name__,
                        'exception_message': str(e),
                        'traceback': traceback.format_exc(),
                        'function': func.__name__,
                        'args': self._safe_repr(args),
                        'kwargs': self._safe_repr(kwargs)
                    }
                    # Re-raise the exception
                    raise

            return wrapper

        return decorator

    def _get_identifier(self, func: Callable, args: tuple, kwargs: dict, identifier_param: Optional[str]) -> str:
        """
        Get an identifier for the function call based on the provided parameters.

        Args:
            func: The function being called
            args: Positional arguments
            kwargs: Keyword arguments
            identifier_param: Parameter name to use as identifier

        Returns:
            str: An identifier for this function call
        """
        if identifier_param and identifier_param in kwargs:
            return str(kwargs[identifier_param])

        if identifier_param and args:
            # Try to find the position of the identifier parameter
            try:
                param_names = func.__code__.co_varnames[:func.__code__.co_argcount]
                if identifier_param in param_names:
                    idx = param_names.index(identifier_param)
                    if idx < len(args):
                        return str(args[idx])
            except (AttributeError, IndexError):
                pass

        # Generate a unique identifier using function name and a hash of arguments
        arg_str = self._safe_repr(args)
        kwarg_str = self._safe_repr(kwargs)
        return f"{func.__name__}_{hash(arg_str + kwarg_str)}_{datetime.now().timestamp()}"

    def _safe_repr(self, obj: Any) -> str:
        """
        Create a safe string representation of an object.

        Args:
            obj: The object to represent

        Returns:
            str: A string representation of the object
        """
        try:
            return str(obj)
        except Exception:
            return f"<unprintable object of type {type(obj).__name__}>"

    def get_log(self) -> Dict[str, Any]:
        """
        Get the current exception log.

        Returns:
            Dict[str, Any]: The exception log
        """
        return self._exception_log.copy()

    def clear_log(self) -> None:
        """Clear the exception log."""
        self._exception_log.clear()

    def get_formatted_log(self, indent: int = 2) -> str:
        """
        Get the exception log formatted as JSON.

        Args:
            indent (int): Number of spaces for JSON indentation

        Returns:
            str: Formatted JSON string
        """
        return json.dumps(self._exception_log, indent=indent)

    def get_exception_count(self) -> int:
        """
        Get the number of exceptions logged.

        Returns:
            int: Number of exceptions
        """
        return len(self._exception_log)

    def get_exceptions_by_type(self) -> Dict[str, int]:
        """
        Get a count of exceptions grouped by exception type.

        Returns:
            Dict[str, int]: Counts of each exception type
        """
        counts: Dict[str, int] = {}
        for exc_info in self._exception_log.values():
            exc_type = exc_info.get('exception_type', 'Unknown')
            counts[exc_type] = counts.get(exc_type, 0) + 1
        return counts


