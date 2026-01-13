"""Define helper functions for handlers."""
import prompt_toolkit as pt

from ..config import baseConf
from ..utils import info_print
from ..OwegaSession import OwegaSession as ps
from ..colors import clrtxt
# from ..conversation import Conversation

def helper_toggle(
    config_key: str,
    given: str = "",
    silent: bool = False,
    description: str = ""
) -> bool:
    """Generic handler for toggling options."""
    given = given.strip()
    if given.lower() in ["on", "true", "enable", "enabled"]:
        baseConf[config_key] = True
        if not silent:
            info_print(f"{description} enabled.")
        return True

    if given.lower() in ["off", "false", "disable", "disabled"]:
        baseConf[config_key] = False
        if not silent:
            info_print(f"{description} disabled.")
        return False

    baseConf[config_key] = (not baseConf.get(config_key, False))
    if not silent:
        status = 'enabled' if baseConf[config_key] else 'disabled'
        info_print(f"{description} {status}.")
    return baseConf[config_key]


def helper_float_value(
    config_key: str,
    given: str = "",
    silent: bool = False,
    min_val: float = 0.0,
    max_val: float = 2.0,
    default_val: float = 1.0,
    description: str = ""
) -> float:
    prev_val = baseConf.get(config_key, default_val)
    given = given.strip()
    prompt_str = '\n' + clrtxt("magenta", f" {description} ") + ': '
    new_value = default_val
    try:
        new_value = float(given)
    except ValueError:
        if not silent:
            info_print(
                f"Current {description}: "
                f"{baseConf.get(config_key, default_val)}"
            )
            info_print(
                f"New {description} value "
                f"({min_val} - {max_val}, defaults {default_val})"
            )
        try:
            if ps['float'] is not None:
                new_value = ps['float'].prompt(pt.ANSI(prompt_str)).strip()
            else:
                new_value = input(prompt_str).strip()
        except (ValueError, KeyboardInterrupt, EOFError):
            if not silent:
                info_print(f"Invalid {description}.")
            return prev_val
    new_value = float(new_value)
    baseConf[config_key] = new_value
    if new_value > max_val:
        if not silent:
            info_print(f"Value too high, capping to {max_val}")
        baseConf[config_key] = max_val
    elif new_value < min_val:
        if not silent:
            info_print(f"Value too low, capping to {min_val}")
        baseConf[config_key] = min_val
    this_val = baseConf.get(config_key, default_val)
    if not silent:
        info_print(f"Set {description} to {this_val}")
    return this_val
