"""Color utility functions for Owega."""

def clr(color: str) -> str:
    """
    Return the ANSI escape sequence for the given color.

    Args:
        color: The color name to get the ANSI code for.
            Valid colors: red, green, yellow, blue, magenta, cyan, white, reset

    Returns:
        The ANSI escape sequence string for the specified color.
    """
    esc = '\033['
    colors = {
        "red": f"{esc}91m",
        "green": f"{esc}92m",
        "yellow": f"{esc}93m",
        "blue": f"{esc}94m",
        "magenta": f"{esc}95m",
        "cyan": f"{esc}96m",
        "white": f"{esc}97m",
        "reset": f"{esc}0m",
    }
    return colors[color]


def clrtxt(color: str, text: str) -> str:
    """
    Format text in color between square brackets.

    Args:
        color: The color name to use.
        text: The text to be colored.

    Returns:
        A string with the text enclosed in square brackets
        and colored with ANSI codes.
    """
    return "[" + clr(color) + text + clr("reset") + "]"
