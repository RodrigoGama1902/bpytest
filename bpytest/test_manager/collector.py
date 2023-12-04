import os

from pathlib import Path

from ..test_manager import TestFile

from .print_helper import print_selected_functions

class Collector:

    test_files : list[TestFile] = []
    
    ignore_dirs : list[str] = [
        "__pycache__", 
        ".git", 
        ".vscode", 
        ".idea", 
        ".pytest_cache", 
        "venv", 
        "build", 
        "dist", 
        "node_modules", 
        ".venv"]
    
    path : Path
    
    def __init__(self, path, selected_functions = []):
        self.path = path
 
        if path.is_file():
            self.test_files.append(TestFile(path, selected_functions))
        if path.is_dir():
            self.test_files = [TestFile(path, selected_functions) for path in self.get_py_files_recursive(path)]

        print_selected_functions(
            self.get_total_collected_tests(),
            self.get_total_deselected_tests(),
            self.get_total_selected_tests()
        )
    
    def get_total_collected_tests(self) -> int:
        
        total = 0

        for test in self.test_files:
            total += len(test.functions_found)

        return total
    
    def get_total_selected_tests(self) -> int:

        total = 0

        for test in self.test_files:
            total += len(test.selected_functions)

        return total
    
    def get_total_deselected_tests(self) -> int:

        total = 0

        for test in self.test_files:
            total += len(test.functions_found) - len(test.selected_functions)

        return total
    
    def get_py_files_recursive(self, path):

        py_files = []
        for root, dirs, files in os.walk(path):
            
            if any(ignore_dir in root for ignore_dir in self.ignore_dirs):
                continue
            
            for file in files:
                if not file.endswith(".py"):
                    continue
                if not "_test.py" in file or "test_" in file:
                    continue

                py_files.append(Path(root, file))

        return py_files