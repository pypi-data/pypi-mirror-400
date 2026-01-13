"""Gather all the handlers."""
import importlib
import pathlib
import os

from ..conversation import Conversation
from ..handlerBase import handler_helps, handlers, items
from ..utils import print_help, debug_print


# prints help
def handle_help(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /help."""
    # removes linter warning about unused arguments
    if temp_file:
        pass
    if given:
        pass
    if temp_is_temp:
        pass
    if silent:
        pass
    print_help(handler_helps)
    return messages


item_help = {
    "fun": handle_help,
    "help": "Shows this help",
    "commands": ["help"],
}


def void_func(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Void function."""
    # removes linter warning about unused arguments
    if temp_file:
        pass
    if given:
        pass
    if temp_is_temp:
        pass
    if silent:
        pass
    return messages


def auto_discover_handlers() -> None:
    """Automatically discover and load all handler modules."""
    current_dir = pathlib.Path(__file__).parent
    for file in sorted(current_dir.glob("handle_*.py")):
        module_name = f".{file.stem}"
        try:
            module = importlib.import_module(module_name, package=__package__)

            # Look for item_* variables
            for attr_name in dir(module):
                if attr_name.startswith("item_"):
                    item = getattr(module, attr_name)
                    if isinstance(item, dict) and "fun" in item:
                        if item not in items:
                            items.append(item)

        except Exception as e:
            debug_print(f"Warning: Failed to load {file.stem}: {e}")


def populate() -> None:
    """Gather all the handlers."""
    # Add help item manually
    items.append(item_help)

    # Autodiscover other commands
    auto_discover_handlers()

    # Populate handler dict from items
    for item in items:
        for command in item.get('commands', []):
            handler_helps[command] = item.get('help', '')
            handlers[command] = item.get('fun', void_func)


populate()
