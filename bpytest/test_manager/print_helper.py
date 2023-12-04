import os

from colorama import Fore, Style
from .entity import TestUnit

def print_header(text : str, color : str = "WHITE", bold = True):

    color = getattr(Fore, color.upper(), "") # Dynamic Fore.color retrive
    if not color:
        raise Exception("Fore Color not found")

    size = os.get_terminal_size()
    print(color + (Style.BRIGHT if bold else "") +'{s:{c}^{n}}'.format(s= " " + text + " ",n=size.columns,c='=')+ Fore.RESET + Style.RESET_ALL)

def print_failed(test_list : list[TestUnit]):

    for test in test_list:
        if not test.success:
            print("----------------------------------------------------------------------")
            test.print_log()

def print_selected_functions(
        total_collected_tests : int, 
        total_deselected_tests : int, 
        total_selected_tests : int):

    print((f"{Style.BRIGHT}collected {str(total_collected_tests)} items / "
            f"{str(total_deselected_tests)} deselected / "
            f"{str(total_selected_tests)} selected \n {Style.RESET_ALL}")
            )

    