
from pathlib import Path
from colorama import Fore

from enum import Enum

from typing import Callable
from dataclasses import dataclass, field

class RunnerType(Enum):

    BACKGROUND = "background"
    RUNTIME = "runtime"
       
class CollectorString:
    
    collector_string : str
    unit : str = ""
    directory : Path
    path : Path
    
    def __init__(self, collector_string : str):
        
        self.collector_string = collector_string
        self.path = Path(collector_string.split("::")[0]).absolute()
        
        if self.path.is_file():
            self.directory = self.path.parent
        else:
            self.directory = self.path
        
        if "::" in self.collector_string:
            self.unit = self.collector_string.split("::")[1]
        
    def __str__(self):
        return self.collector_string
    
@dataclass
class BpyTestConfig:
    '''Class that represents the configuration of the test session.
    
    :param pythonpath: Path python cwd
    :param nocapture: Show test log
    :param toggle_console: Toggle console before and after running tests
    :param runner_type: Define the test process mode to be used, background or runtime.
        In background mode, the test is run in a subprocess, in runtime mode, the test is run in
        the current blender process.
    :param module_list: List of modules to be loaded before running the tests
    :param blender_exe: Path to blender executable
    
    '''

    pythonpath : Path = field(default=Path.cwd())
    nocapture : bool = field(default=False)
    toggle_console : bool = field(default=False)
    module_list : str = field(default="")
    runner_type : RunnerType = field(default=RunnerType.BACKGROUND)
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
        
        self.pythonpath = Path(pyproject_toml.get("pythonpath")).absolute()
        self.nocapture = pyproject_toml.get("nocapture", False)
        self.toggle_console = pyproject_toml.get("toggle_console", False)
        self.raise_error = pyproject_toml.get("raise_error",False)
        self.module_list = pyproject_toml.get("module_list", "")
        self.runner_type = RunnerType(pyproject_toml.get("runner_type", "background"))
        self.blender_exe = Path(pyproject_toml.get("blender_exe", Path.cwd()))
        
class TestUnit:

    function_name : str
    success : bool
    test_filepath : Path
    result_lines : list[str]
    collector_string : CollectorString 

    def __init__(self, test_filepath : Path, function_name : str):
        
        self.result_lines = []
        self.test_filepath = test_filepath
        self.function_name = function_name
        self.collector_string = CollectorString(f"{self.test_filepath}::{self.function_name}")
        
        self.success = False
     
    def print_log(self):
        for line in self.result_lines:
            print(line)
                
    def __repr__(self) -> str:

        color = Fore.GREEN if self.success else Fore.RED
        return f'"{self.test_filepath}" {self.function_name} {color} {"[PASSED]" if self.success else "[FAILED]"}{Fore.RESET}'

@dataclass
class Fixture:
    
    name : str
    scope : str
    function : Callable
class TestFile:

    filepath : Path
    test_units : list[TestUnit]
    fixtures : list[Fixture]
    
    def __init__(self, filepath):

        self.filepath = filepath
        self.test_units = self.parse_test_units()

    def parse_test_units(self) -> list[TestUnit]:

        test_units = []

        with open(self.filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                if not "def test_" in line:
                    continue
                
                function_name = line.split("def ")[1].split("(")[0] 
                test_units.append(TestUnit(self.filepath, function_name))

        return test_units
    
    def load_fixtures(self):
        
        with open(self.filepath, "r") as file:
            lines = file.readlines()
            for line in lines:
                if not "@fixture" in line:
                    continue
                
                fixture_name = line.split("@fixture")[1].split("(")[0].strip()
                fixture_scope = line.split("(")[1].split(")")[0].strip()
                
                self.fixtures.append(Fixture(fixture_name, fixture_scope, None))
    
    
        

    
    