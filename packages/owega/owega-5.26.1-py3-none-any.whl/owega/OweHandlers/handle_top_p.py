"""Handle /top_p."""
from ..conversation import Conversation
from ..constants import OWEGA_DEFAULT_TOP_P as ODTP
from .helpers import helper_float_value


# change top_p value
def handle_top_p(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    f"""Handle /top_p.

    Command description:
        Sets the top_p value (0.0 - 1.0, defaults {ODTP}).

    Usage:
        /top_p [top_p]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_float_value(
        "top_p",
        given,
        silent,
        0.0,
        1.0,
        ODTP,
        "top_p"
    )
    return messages


item_top_p = {
    "fun": handle_top_p,
    "help": f"sets the top_p value (0.0 - 1.0, defaults {ODTP})",
    "commands": ["top_p"],
}
