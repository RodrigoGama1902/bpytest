import os
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .entity import TestUnit
class BColors(Enum):
    """Enum that represents the colors for the terminal"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BRIGHT = "\033[1m"
    WHITE = "\033[97m"


def print_header(text: str, color: BColors = BColors.WHITE, bold: bool = True):
    """Prints a header with the given text"""

    color = getattr(BColors, color.name.upper())
    if not color:
        raise ValueError(f"Color {color} not found")

    try:
        size = os.get_terminal_size()
    except OSError:
        # Return a default size if getting terminal size fails
        size = os.terminal_size((80, 24))  # Default to 80x24 characters
    print(
        color.value
        + (BColors.BOLD.value if bold else "")
        + "{s:{c}^{n}}".format(s=" " + text + " ", n=size.columns, c="=")
        + BColors.ENDC.value
    )


def print_failed(test_list: list["TestUnit"]):

    for test in test_list:
        if not test.success:
            print(
                "----------------------------------------------------------------------"
            )
            test.print_log()


def print_selected_functions(
    total_collected_tests: int,
    total_deselected_tests: int,
    total_selected_tests: int,
):

    print(
        (
            f"{BColors.BRIGHT.value}collected {str(total_collected_tests)} items / "
            f"{str(total_deselected_tests)} deselected / "
            f"{str(total_selected_tests)} selected \n {BColors.ENDC.value}"
        )
    )
    
def bpyprint(string : Any):
    """Prints a string to the console with a specific color and formatting."""
    print(string)
