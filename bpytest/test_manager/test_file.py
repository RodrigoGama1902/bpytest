
from pathlib import Path

class TestFile:

    selected_functions : list[str] = []
    functions_found : list[str] = []

    filepath : Path
    
    def __init__(self, filepath, selected_functions = []):

        self.filepath = filepath
        self.functions_found = self.parse_test_function_names()
        self.selected_functions = self.load_selected_functions(selected_functions)

    def parse_test_function_names(self):

        functions = []

        with open(self.filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                if not "def test_" in line:
                    continue
                function_name = line.split("def ")[1].split("(")[0]
                functions.append(function_name)
        
        return functions
    
    def load_selected_functions(self, selected_functions):

        functions = []

        for function_name in self.functions_found:
            if not selected_functions or selected_functions == [""]:
                functions.append(function_name)
                continue
            if function_name in selected_functions:
                functions.append(function_name)
                continue
        
        return functions