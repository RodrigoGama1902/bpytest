import sys
from typing import Any


def bpyprint(string: Any, flush: bool = True):
    """Prints a string to the console with a specific color and formatting."""
    print("[bpytest]" + str(string))
    if flush:
        sys.stdout.flush()


def is_bpyprint(string: str) -> bool:
    """Check if the string is from bpyprint"""
    return string.startswith("[bpytest]")


def decode_bpyprint(string: str) -> str:
    """Decode the string from bpyprint"""
    return string.replace("[bpytest]", "")
