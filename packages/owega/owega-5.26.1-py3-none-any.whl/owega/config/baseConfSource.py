"""Owega base configuration module."""

import os

import json5 as json
from ..constants import (
    OWEGA_DEFAULT_PROMPT,
    OWEGA_DEFAULT_MAX_TOKENS,
    OWEGA_DEFAULT_TEMPERATURE,
    OWEGA_DEFAULT_TOP_P,
    OWEGA_DEFAULT_FREQUENCY_PENALTY,
    OWEGA_DEFAULT_PRESENCE_PENALTY
)
from ..colors import clrtxt

baseModels = [
    "openai:gpt-4o",
    "mistral:open-mixtral-8x22b",
    "mistral:mistral-large-latest",
    "chub:mixtral",
    "chub:mars",
    "chub:mercury",
    "anthropic:claude-3-7-sonnet-latest",
    "openrouter:deepseek/deepseek-chat-v3-0324:free",
    "xai:grok-2-1212",
    "custom:deepseek/deepseek-chat-v3-0324:free@https://openrouter.ai/api/v1"
]
baseConf = {
    "api_key": "",  # OpenAI API key
    "organization": "",  # OpenAI organization
    "mistral_api": "",  # Mistral API key
    "chub_api": "",  # Chub Venus API key
    "claude_api": "",  # Anthropic Claude API key
    "xai_api": "",  # xAI API key
    "openrouter_api": "",  # OpenRouter API key
    "custom_api": "",  # Custom API key (for custom endpoint)
    "custom_endpoint": "",  # Custom endpoint (should be OpenAI-compatible)
    "default_prompt": (  # Default context prompt
        OWEGA_DEFAULT_PROMPT
    ),
    "model": baseModels[0],  # default model (first entry in baseModels)
    "temperature": OWEGA_DEFAULT_TEMPERATURE,  # AI Temperature (randomness)

    # AI generation parameters (top_p and penalties)
    "top_p": OWEGA_DEFAULT_TOP_P,
    "frequency_penalty": OWEGA_DEFAULT_FREQUENCY_PENALTY,
    "presence_penalty": OWEGA_DEFAULT_PRESENCE_PENALTY,

    "max_tokens": OWEGA_DEFAULT_MAX_TOKENS,  # Max tokens in response
    "available_models": baseModels,  # Available models
    "debug": False,  # Debug mode
    "commands": False,  # Command execution
    "web_access": False,  # Web access
    "lts_enabled": False,  # Long-term souvenirs feature
    "time_awareness": False,  # Save current date and time with each user msg
    "estimation": True,  # Cost and tokens estimation
    "tts_enabled": False,  # Default TTS status
    "fancy": True,  # Fancy print (requires python-rich)

    # Pre/post message injections
    "pre_user": "",
    "post_user": "",
    "pre_assistant": "",
    "post_assistant": "",
    "pre_system": "",
    "post_system": "",

    # Pre/post history injections: list of message dicts
    "pre_history": [],
    "post_history": [],
}


def get_home_dir() -> str:
    """Get the user home directory, cross-platform."""
    return os.path.expanduser('~')


def debug_print(text: str) -> None:
    """
    Print a message if debug is enabled.

    Parameters
    ----------
    text : str
        The text to print if debug is enabled.
    """
    if baseConf.get("debug", False):
        print(' ' + clrtxt("magenta", " DEBUG ") + ": " + text)


def info_print(msg) -> None:
    """Print an info message."""
    print('  ' + clrtxt("cyan", " INFO ") + ": ", end='')
    print(msg)


def get_conf(conf_path: str = "") -> None:
    """
    Load the config from a config file.

    Parameters
    ----------
    conf_path : str, optional
        The path to the config file to load.
    """

    config_files = []

    def this_add_file(path):
        expanded = os.path.expanduser(path)
        if os.path.isfile(expanded):
            if expanded not in config_files:
                config_files.append(expanded)
        elif os.path.isdir(expanded):
            this_add_dir(expanded)

    def this_add_dir(path):
        expanded = os.path.expanduser(path)
        if os.path.isdir(expanded):
            for root, dirs, files in os.walk(expanded):
                _ = dirs
                for file in files:
                    if file.endswith('.json') or file.endswith('.json5'):
                        this_add_file(os.path.join(root, file))
        elif os.path.isfile(expanded):
            this_add_file(expanded)

    def this_add_generic(path):
        if not path:
            return

        expanded = os.path.expanduser(path)

        if not os.path.exists(expanded):
            return

        if os.path.isfile(expanded):
            this_add_file(expanded)
        elif os.path.isdir(expanded):
            this_add_dir(expanded)

    this_add_file("~/.owega.json")
    this_add_dir("~/.config/owega")

    this_add_generic(conf_path)

    config_files.sort()
    debug_print(f"{config_files}")

    if not config_files:
        return

    new_debug_status = baseConf.get('debug', False)
    for file in config_files:
        debug_print(f"Loading {file}...")
        with open(file) as f:
            try:
                conf_dict = json.load(f)
            except ValueError as e:
                debug_print("Error, file dismissed.")
                debug_print(f"Error: {e}")
                continue
            if isinstance(conf_dict, dict):
                for k, v in conf_dict.items():
                    try:
                        if k == "debug":
                            new_debug_status = v
                        else:
                            baseConf[k] = v
                    except ValueError:
                        pass

    baseConf["debug"] = new_debug_status


def list_models() -> None:
    """
    List available models.

    Notes
    -----
    This function only prints from the config, it does not return anything.
    Config should have been loaded before calling this function.
    """
    info_print("Available models:")
    for index, model in enumerate(baseConf.get("available_models", [])):
        info_print(f"    [{index}]: {model}")
