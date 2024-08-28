from datetime import timedelta, datetime
import platform
import functools
from typing import Literal

from rich.text import TextType


@functools.cache
def is_wsl(v: str = platform.uname().release) -> int:
    """
    detects if Python is running in WSL
    """

    if v.endswith("-Microsoft"):
        return 1
    elif v.endswith("microsoft-standard-WSL2"):
        return 2

    return 0


def nicer_string(in_string: str) -> str:
    retval = in_string.capitalize()
    retval = retval.replace('_', ' ')
    return retval


def color_str_from_dict(inp: str, in_value: dict[str, TextType],
                        color: Literal['blue', 'green', 'orange']= 'blue',
                        is_timedelta=False,
                        is_timestamp=False) -> str:

    string = nicer_string(inp)
    value = in_value.get(inp, None)
    if not value:
        color = 'red'
        return f"{string}: [{color}]{value}[/]"
    retval = f"{string}: [{color}]{value}[/]"
    if is_timedelta:
        retval = f"{string}: [{color}]{timedelta(int(value))}[/]"
    if is_timestamp:
        retval = f"{string}: [{color}]{datetime.fromtimestamp(int(value))}[/]"

    return retval