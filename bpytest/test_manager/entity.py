
from pathlib import Path
from colorama import Fore

from enum import Enum
from dataclasses import dataclass, field

class TestMode(Enum):

    BACKGROUND = "background"
    RUNTIME = "runtime"

@dataclass
class ConfigFile:
    '''Reads pyproject.toml file
    
    :param pythonpath: Path python cwd
    :param display_output: Show test log
    :param selected_functions: List of selected functions to test functions to run
    :param test_search_relative_path: Path to search for tests, relative to python cwd, if empty, search in python cwd
    :param toggle_console: Toggle console before and after running tests
    :param test_mode: Define the test process mode to be used, background or runtime.
        In background mode, the test is run in a subprocess, in runtime mode, the test is run in
        the current blender process.
    
    '''

    pythonpath : Path = field(default=Path.cwd())
    test_search_relative_path : Path = field(default=Path.cwd())
    display_output : bool = field(default=False)
    selected_functions : list[Path] = field(default_factory=list)
    toggle_console : bool = field(default=False)
    module_list : str = field(default="")
    test_mode : TestMode = field(default=TestMode.BACKGROUND)
    blender_exe : Path = field(default=Path.cwd())

    def load_from_pyproject_toml(self, pyproject_toml_path : Path):
        '''Loads the config file from pyproject.toml'''

        import toml # type: ignore

        try:
            if not pyproject_toml_path.exists():
                raise Exception("pyproject.toml not found")
            
            pyproject_toml = toml.load(pyproject_toml_path)["tool"]["bpytest"]
        except KeyError:
            print("tool.bpytest not found")
            return
        
        self.pythonpath = pyproject_toml.get("pythonpath")
        self.test_search_relative_path = pyproject_toml.get("test_search_relative_path", "")
        self.display_output = pyproject_toml.get("display_output", False)
        self.selected_functions = pyproject_toml.get("selected_functions", [])
        self.toggle_console = pyproject_toml.get("toggle_console", False)
        self.raise_error = pyproject_toml.get("raise_error",False)
        self.module_list = pyproject_toml.get("module_list", "")
        self.test_mode = TestMode(pyproject_toml.get("test_mode", "background"))
        self.blender_exe = Path(pyproject_toml.get("blender_exe", Path.cwd()))

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