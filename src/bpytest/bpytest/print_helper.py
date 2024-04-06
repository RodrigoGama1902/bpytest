import os

from .entity import BColors, TestUnit


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


def print_failed(test_list: list[TestUnit]):

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
