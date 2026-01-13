"""Utilities that don't fit anywhere else."""
import os
import sys
import tempfile
from typing import Literal

import json5 as json
import openai

try:
    import sounddevice as sd
    import soundfile as sf
    audio_lib = "sounddevice"
except ImportError:
    sd = None
    sf = None
    audio_lib = None

try:
    import tiktoken
except ModuleNotFoundError:
    def __internal_get_tokens(s: str) -> int:
        return len(s) // 4
else:
    def __internal_get_tokens(s: str) -> int:
        encoder = tiktoken.encoding_for_model("gpt-4")
        return len(encoder.encode(s))

from . import getLogger
from .config import baseConf, get_home_dir, info_print, debug_print
from .colors import clrtxt
from .conversation import Conversation

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.theme import Theme
except ModuleNotFoundError:
    def markdown_print(s: str) -> None:
        print(s)
else:
    console = Console()

    _owega_themes = {
        "system": {
            "markdown.em": "italic grey58",
        }
    }

    def owega_apply_theme():
        while (len(console._theme_stack._entries) > 1):
            console.pop_theme()

        global_theme = {}
        for theme in _owega_themes.values():
            try:
                for key, value in theme.items():
                    global_theme[key] = value
            except Exception:
                pass
        theme = Theme(global_theme)
        console.push_theme(theme)

    def owega_reload_themes():
        for theme_name in [
            key
            for key in baseConf.keys()
            if (key.startswith("theme.") or (key == "theme"))
        ]:
            _owega_themes[theme_name] = baseConf.get(theme_name, {}).copy()

    def markdown_print(s: str) -> None:
        if baseConf.get("fancy", False):
            if (len(console._theme_stack._entries) <= 1):
                owega_reload_themes()
                owega_apply_theme()
            console.print(Markdown(s))
        else:
            print(s)


def set_term_title(new_title: str) -> None:
    print(f"\033]0;{new_title}\a", end='')


def get_temp_file() -> str:
    """Get a temp file location."""
    tmp = tempfile.NamedTemporaryFile(
        prefix="owega_temp.",
        suffix=".json",
        delete=False
    )
    filename = tmp.name
    tmp.close()
    return filename


def command_text(msg) -> str:
    """Print a command message."""
    return ' ' + clrtxt("red", "COMMAND") + ": " + msg


def success_msg() -> str:
    """Return the standard success message."""
    return '  ' + clrtxt("cyan", " INFO ") + ": Owega exited successfully!"


def genconfig(conf_path="") -> None:
    """Generate the config file if it doesn't exist already."""
    _ = conf_path
    conf_dir = os.path.expanduser('~/.config/owega')
    conf_file = os.path.join(conf_dir, 'config.json5')
    conf_file_api = os.path.join(conf_dir, 'api.json5')
    if not os.path.exists(conf_dir):
        os.mkdir(conf_dir)
    else:
        if not os.path.isdir(conf_dir):
            info_print('Error: "~/.config/owega" is not a directory.')
    config_noapi = {}
    config_api = {}
    for key, val in baseConf.items():
        if "api" in key.lower():
            if not isinstance(val, str):
                val = ""
            config_api[key] = val
        else:
            config_noapi[key] = val

    if not os.path.exists(conf_file_api):
        with open(conf_file_api, "w") as f:
            f.write('// vim: set ft=json5:\n')
            f.write(str(json.dumps(config_api, indent=4)))
        info_print(f"saved api keys as ~/.config/owega/api.json5 !")

    should_write = True
    if os.path.isfile(conf_file):
        should_write = False
        print(
            clrtxt('red', ' WARNING ')
            + ": YOU ALREADY HAVE A CONFIG FILE AT "
            + "~/.config/owega/config.json5"
        )
        print(
            clrtxt('red', ' WARNING ')
            + ": DO YOU REALLY WANT TO OVERWRITE IT???")

        inps = clrtxt("red", "   y/N   ") + ': '
        inp = input(inps).lower().strip()
        if inp:
            if inp[0] == 'y':
                should_write = True

    if should_write:
        with open(conf_file, "w") as f:
            f.write('// vim: set ft=json5:\n')
            f.write(str(json.dumps(config_noapi, indent=4)))
        info_print("saved configuration as ~/.config/owega/config.json5 !")
        return

    info_print("Sorry, not sorry OwO I won't let you nuke your config file!!!")


def play_opus(location: str) -> None:
    """Play an OPUS audio file."""
    _ = location
    if audio_lib == "sounddevice" and sf is not None and sd is not None:
        try:
            data, fs = sf.read(location)
            sd.play(data, fs)
            sd.wait()  # wait until file is done playing
        except Exception as e:
            info_print(f"Could not play audio: {e}")
    else:
        info_print("Could not play audio, missing audio library.")


def tts_to_opus(
    loc: str,
    text: str,
    voice: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'] = 'nova'
) -> None:
    """Generate TTS audio from given text and save it to an opus file."""
    tts_answer = openai.audio.speech.create(
        model='tts-1',
        voice=voice,
        input=text
    )
    tts_answer.write_to_file(loc)


def play_tts(
    text: str,
    voice: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'] = 'nova'
) -> None:
    """Generate TTS audio from given text and play it."""
    tmpfile = tempfile.NamedTemporaryFile(
        prefix="owegatts.",
        suffix=".opus",
        delete=False
    )
    tmpfile.close()
    tts_to_opus(tmpfile.name, text, voice)
    play_opus(tmpfile.name)
    os.remove(tmpfile.name)


def estimated_tokens(ppt: str, messages: Conversation, functions: list) -> int:
    """Estimate the history tokens."""
    try:
        total_tokens = 0

        # Count prompt tokens if provided
        if ppt:
            total_tokens += __internal_get_tokens(ppt)

        # Count message tokens
        for msg in messages.get_messages():
            content = msg.get('content', '')
            if isinstance(content, str):
                total_tokens += __internal_get_tokens(content)
            elif isinstance(content, list):
                # Handle vision messages
                for item in content:
                    if item.get('type') == 'text':
                        total_tokens += __internal_get_tokens(
                            item.get('text', '')
                        )
                    elif item.get('type') == 'image_url':
                        # Rough estimate for images (varies by size)
                        total_tokens += 85  # Low detail estimate

        # Count function/tool tokens (rough estimate)
        if functions:
            for func in functions:
                # Count function definition tokens
                func_str = str(func.get('function', {}))
                total_tokens += __internal_get_tokens(func_str)

        # Add overhead for message formatting (~4 tokens per message)
        total_tokens += len(messages.get_messages()) * 4
        return total_tokens
    except Exception as e:
        logger = getLogger.getLogger(__name__, baseConf.get("debug", False))
        logger.info("An error has occured while estimating tokens:")
        logger.info(e)
        return 0


def estimated_cost_dual(
    input_tokens: int, model: str, output_tokens: int = 4096, provider: str = ""
) -> tuple[float, float]:
    """Calculate estimated cost based on token counts."""
    from .pricing import get_model_pricing

    input_price, output_price = get_model_pricing(model, provider)

    if input_price == 0 and output_price == 0:
        return 0.0, 0.0

    return ((input_tokens * input_price), (output_tokens * output_price))


def estimated_cost(
    input_tokens: int, model: str, output_tokens: int = 4096, provider: str = ""
) -> float:
    """Calculate estimated combined cost based on token counts."""
    return sum(estimated_cost_dual(
        input_tokens,
        model,
        output_tokens,
        provider
    ))


def estimated_tokens_and_cost_dual(
    ppt: str,
    messages: Conversation,
    functions: list,
    model: str,
    output_tokens: int = 4096,
    provider: str = ""
) -> tuple[int, float, int, float]:
    """Estimate input tokens and cost with provider support."""
    input_tokens = estimated_tokens(ppt, messages, functions)
    in_cost, out_cost = estimated_cost_dual(
        input_tokens, model, output_tokens, provider
    )
    return (input_tokens, in_cost, output_tokens, out_cost)


def estimated_tokens_and_cost(
    ppt: str,
    messages: Conversation,
    functions: list,
    model: str,
    output_tokens: int = 4096,
    provider: str = ""
) -> tuple[int, float]:
    """Estimate input tokens and combined cost with provider support."""
    input_tokens, in_cost, _, out_cost = estimated_tokens_and_cost_dual(
        ppt, messages, functions, model, output_tokens, provider
    )
    return (input_tokens, (in_cost + out_cost))


def do_quit(
    msg="", value=0, temp_file="", is_temp=False, should_del=False
) -> None:
    """Quit and delete the given file if exists."""
    if (temp_file):
        if should_del:
            try:
                os.remove(temp_file)
            except OSError:
                pass
        else:
            if is_temp:
                try:
                    with open(temp_file, 'r') as f:
                        contents = json.loads(f.read())
                        if isinstance(contents, dict):
                            if not (
                                (len(contents.get("messages", [])) > 0)
                                or (len(contents.get("souvenirs", [])) > 0)
                            ):
                                os.remove(temp_file)
                except (OSError, ValueError):
                    pass
    if (msg):
        print()
        print(msg)
    sys.exit(value)


def print_help(commands_help=None) -> None:
    """Print the command help."""
    if commands_help is None:
        commands_help = {}
    commands = list(commands_help.keys())
    longest = 0
    for command in commands:
        if len(command) > longest:
            longest = len(command)
    longest += 1
    print()
    info_print(
        "Enter your question after the user prompt, "
        + "and it will be answered by OpenAI")
    info_print("other commands are:")
    for cmd, hstr in commands_help.items():
        command = '/' + cmd
        info_print(f"   {command:>{longest}}  - {hstr}")
    print()


def user_prefix() -> str:
    out_str = ""
    out_str += '\n'
    out_str += "  " + clrtxt("yellow", " USER ") + ": \n"
    return out_str


def assistant_prefix() -> str:
    out_str = ""
    out_str += '\n'
    out_str += " " + clrtxt("magenta", " Owega ") + ": \n"
    return out_str


def render_user(content: str) -> None:
    print(user_prefix())
    markdown_print(content)


def render_assistant(content: str) -> None:
    print(assistant_prefix())
    markdown_print(content)


def render_conversation_buffer(conv: Conversation) -> None:
    for message in conv.printbuffer_get():
        role = message.get("role", "unknown")
        if role == "user":
            render_user(message.get("content", ""))
        elif role == "assistant":
            render_assistant(message.get("content", ""))
    conv.printbuffer_clear()
