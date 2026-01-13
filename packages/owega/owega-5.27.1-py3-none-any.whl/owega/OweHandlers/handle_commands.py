"""Handle /commands."""
from ..conversation import Conversation
from ..OwegaFun import existingFunctions
from .helpers import helper_toggle


# enables/disables command execution
def handle_commands(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /commands.

    Command description:
        Toggles command execution / file creation.

    Usage:
        /commands [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    status = helper_toggle("commands", given, silent, "Command execution")
    if status:
        existingFunctions.enableGroup("utility.system")
    else:
        existingFunctions.disableGroup("utility.system")

    return messages


item_commands = {
    "fun": handle_commands,
    "help": "toggles command execution / file creation",
    "commands": ["commands"],
}
