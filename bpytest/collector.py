import os

from pathlib import Path

from .entity import TestFile, TestUnit, CollectorString
from .print_helper import print_selected_functions

class Collector:

    test_files : list[TestFile] = []
    test_units : list[TestUnit] = []
    selected : list[TestUnit] = []
    
    _collector_string_unit : CollectorString
    
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
    
    def __init__(self, collector_string : CollectorString, keyword = ""):
        
        self._collector_string = collector_string
                    
        if self._collector_string.path.is_file():
            self.test_files.append(TestFile(self._collector_string.path))
        if self._collector_string.path.is_dir():
            self.test_files = [TestFile(path) for path in self.get_py_files_recursive(self._collector_string.path)]
            
        self.test_units = self._load_all_test_units(self.test_files)
        
        self.selected = self._filter_by_collector_string(self.test_units, self._collector_string)
        self.selected = self.filter_by_keyword(self.selected, keyword)
                        
        print_selected_functions(
            len(self.test_units),
            len(self.test_units) - len(self.selected),
            len(self.selected)
        )
        
    @staticmethod
    def _load_all_test_units(test_files) -> list[TestUnit]:
        
        test_units = []
        
        for test_file in test_files:
            test_units.extend(test_file.test_units)
            
        return test_units
    
    @staticmethod
    def _filter_by_collector_string(test_units, filter_collector_string : CollectorString) -> list[TestUnit]:
        
        filtered : list[TestUnit] = []
        
        for unit in test_units:
            if not filter_collector_string.path.resolve() == unit.collector_string.path.resolve():
                continue
            
            if filter_collector_string.unit:
                if not filter_collector_string.unit == unit.collector_string.unit:
                    continue
                
            filtered.append(unit)
            
        return filtered
    
    @staticmethod
    def filter_by_keyword(test_units, keyword):

        functions = []
        
        for unit in test_units:
            if keyword in unit.function_name:
                functions.append(unit)

        return functions
                        
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