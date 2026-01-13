"""Handle /presence."""
from ..conversation import Conversation
from ..constants import OWEGA_DEFAULT_PRESENCE_PENALTY as ODPP
from .helpers import helper_float_value


# change presence penalty
def handle_presence(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    f"""Handle /presence.

    Command description:
        Sets the presence penalty (-2.0 - 2.0, defaults {ODPP}).

    Usage:
        /presence [presence]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_float_value(
        "presence_penalty",
        given,
        silent,
        -2.0,
        2.0,
        ODPP,
        "presence penalty"
    )
    return messages


item_presence = {
    "fun": handle_presence,
    "help": f"sets the presence penalty (-2.0 - 2.0, defaults {ODPP})",
    "commands": ["presence"],
}
