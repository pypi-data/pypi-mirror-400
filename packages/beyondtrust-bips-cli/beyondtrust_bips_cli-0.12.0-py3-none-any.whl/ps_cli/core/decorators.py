from functools import wraps
from typing import Any, Callable

from ps_cli.core.utils import valid_uuid

# Confirmation message constants
CONFIRM_DELETE_PREFIX = "Are you sure you want to delete"


def command(func) -> Callable:
    """
    Decorator to mark a method as a command and store its options and aliases.

    Args:
        func (Callable): The function to be decorated as a command.

    Returns:
        Callable: The decorated function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__options__ = getattr(func, "__options__", [])
    wrapper.__aliases__ = getattr(func, "__aliases__", [])
    return wrapper


def option(
    *args,
    default: Any = None,
    type: Any = None,
    action: str = None,
    nargs: str | int = None,
    enforce_uuid: bool = False,
    **kwargs,
) -> Callable:
    """
    Decorator to add an option to a command, storing its args, default, type, etc.

    Args:
        *args (str): The option strings (e.g., "-n", "--name").
        default (Any, optional): The default value for the option. Defaults to None.
        type (Any, optional): The type of the option value. Defaults to None.
        enforce_uuid (bool, optional): If the option should be a valid UUID, if True
            then "type" is not used. Default False.
        **kwargs (Any): Additional keyword arguments for the option.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        if not hasattr(wrapper, "__options__"):
            wrapper.__options__ = []

        option_type = valid_uuid if enforce_uuid else type

        use_action = action in [
            "store_true",
            "store_false",
            "store_const",
            "append_const",
            "count",
        ]

        wrapper_options = {
            "args": args,
            "kwargs": kwargs,
            "default": default,
        }

        if use_action:
            wrapper_options["action"] = action
        else:
            wrapper_options["type"] = option_type
            wrapper_options["nargs"] = nargs

        wrapper.__options__.append(wrapper_options)
        return wrapper

    return decorator


def aliases(*aliases) -> Callable:
    """
    Decorator to add aliases to a command, allowing it to be called with different
    names.

    Args:
        *aliases (str): The alias names for the command.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__aliases__ = aliases
        return wrapper

    return decorator


def confirmation_required(
    message: str = "Are you sure you want to proceed? (y/yes/n): ",
) -> Callable:
    """
    Decorator to prompt the user for confirmation before executing a command.

    Args:
        message (str, optional): The confirmation message to display. Defaults to
            "Are you sure you want to proceed? (y/yes/n): ".

    Returns:
        Callable: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):

            auto_approve_settings = self.app.settings.get(
                "general", "auto_approve", "false"
            )

            auto_approve_app = getattr(self.app.args, "auto_approve", False)

            if auto_approve_settings.lower() == "true" or auto_approve_app:
                return func(self, *args, **kwargs)
            else:
                response = input(message).strip().lower()
                if response not in ("y", "yes"):
                    print("Operation cancelled by user.")
                    return None
                return func(self, *args, **kwargs)

        return wrapper

    return decorator
