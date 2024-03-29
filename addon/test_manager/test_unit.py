
from colorama import Fore, Style

from ..test_manager import TestFile

class TestUnit:

    test_file : TestFile
    function_name : str
    success : bool

    result_lines : list[str]

    def __init__(self, test_file : TestFile, function_name : str):
        
        self.result_lines = []
        self.test_file = test_file
        self.function_name = function_name
        self.success = False
    
    def print_log(self):
        for line in self.result_lines:
            print(line)
    
    def __repr__(self) -> str:

        color = Fore.GREEN if self.success else Fore.RED
        return f'"{self.test_file.filepath}" {self.function_name} {color} {"[PASSED]" if self.success else "[FAILED]"}{Fore.RESET}'