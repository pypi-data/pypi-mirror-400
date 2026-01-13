"""Handle /time."""
from ..conversation import Conversation
from .helpers import helper_toggle


def handle_time(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /time.

    Command description:
        Toggles sending the date and time with each message.
        (time-aware mode)

    Usage:
        /time [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_toggle("time_awareness", given, silent, "Time-aware mode")
    return messages


item_time = {
    "fun": handle_time,
    "help": "toggles sending the date and time with each message (time-aware)",
    "commands": ["time"],
}
