"""Handle /temperature."""
from ..conversation import Conversation
from ..constants import OWEGA_DEFAULT_TEMPERATURE as ODT
from .helpers import helper_float_value


# change temperature
def handle_temperature(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    f"""Handle /temperature.

    Command description:
        Sets the temperature (0.0 - 2.0, defaults {ODT}).

    Usage:
        /temperature [temperature]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_float_value(
        "temperature",
        given,
        silent,
        0.0,
        2.0,
        ODT,
        "temperature"
    )
    return messages


item_temperature = {
    "fun": handle_temperature,
    "help": f"sets the temperature (0.0 - 2.0, defaults {ODT})",
    "commands": ["temperature"],
}
