"""Handle /commands."""
from ..conversation import Conversation
from ..OwegaFun import existingFunctions
from .helpers import helper_toggle


# enables/disables command execution
def handle_web(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /web.

    Command description:
        Toggles web access.

    Usage:
        /web [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    status = helper_toggle("web_access", given, silent, "Web access")
    if status:
        existingFunctions.enableGroup("utility.user")
    else:
        existingFunctions.disableGroup("utility.user")

    return messages


item_web = {
    "fun": handle_web,
    "help": "toggles web access",
    "commands": ["web"],
}
