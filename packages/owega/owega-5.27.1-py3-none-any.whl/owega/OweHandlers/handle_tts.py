"""Handle /tts."""
from ..conversation import Conversation
from .helpers import helper_toggle


# enables/disables the TTS
def handle_tts(
    temp_file: str,
    messages: Conversation,
    given: str = "",
    temp_is_temp: bool = False,
    silent: bool = False
) -> Conversation:
    """Handle /tts.

    Command description:
        Toggles the TTS output.

    Usage:
        /tts [on/true/enable/enabled/off/false/disable/disabled]
    """
    # removes linter warning about unused arguments
    _, _ = temp_file, temp_is_temp
    helper_toggle("tts_enabled", given, silent, "Text-to-speech")
    return messages


item_tts = {
    "fun": handle_tts,
    "help": "enables/disables the TTS",
    "commands": ["tts"],
}
