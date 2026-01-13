"""Handle /lts."""
from ..conversation import Conversation
from ..OwegaFun import existingFunctions
from .helpers import helper_toggle


def handle_lts(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /lts.

    Command description:
        Toggles long-term souvenirs (memory) feature.

    Usage:
        /lts [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    status = helper_toggle("lts_enabled", given, silent, "Long-term souvenirs")
    if status:
        existingFunctions.enableGroup("lts")
    else:
        existingFunctions.disableGroup("lts")

    return messages


item_lts = {
    "fun": handle_lts,
    "help": "toggles long-term souvenirs (memory) feature",
    "commands": ["lts", "memory"],
}
