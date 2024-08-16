import platform
import functools


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