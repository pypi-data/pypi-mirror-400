"""Handle /fancy."""
from ..conversation import Conversation
from .helpers import helper_toggle


def handle_fancy(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /fancy.

    Command description:
        Toggles fancy printing (requires python-rich).

    Usage:
        /fancy [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_toggle("fancy", given, silent, "Fancy printing")
    return messages


item_fancy = {
    "fun": handle_fancy,
    "help": "toggles fancy printing (requires python-rich)",
    "commands": ["fancy"],
}
