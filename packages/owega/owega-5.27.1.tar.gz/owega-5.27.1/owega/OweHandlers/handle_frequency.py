"""Handle /frequency."""
from ..conversation import Conversation
from ..constants import OWEGA_DEFAULT_FREQUENCY_PENALTY as ODFP
from .helpers import helper_float_value


# change frequency penalty
def handle_frequency(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    f"""Handle /frequency.

    Command description:
        Sets the frequency penalty (-2.0 - 2.0, defaults {ODFP}).

    Usage:
        /frequency [frequency]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_float_value(
        "frequency_penalty",
        given,
        silent,
        -2.0,
        2.0,
        ODFP,
        "frequency penalty"
    )
    return messages


item_frequency = {
    "fun": handle_frequency,
    "help": f"sets the frequency penalty (-2.0 - 2.0, defaults {ODFP})",
    "commands": ["frequency"],
}
