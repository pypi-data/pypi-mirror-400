"""Handle /estimation."""
from ..conversation import Conversation
from .helpers import helper_toggle


def handle_estimation(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /estimation.

    Command description:
        Toggles displaying the token estimation.

    Usage:
        /estimation [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_toggle("estimation", given, silent, "Token estimation")
    return messages


item_estimation = {
    "fun": handle_estimation,
    "help": "toggles displaying the token estimation",
    "commands": ["estimation"],
}
