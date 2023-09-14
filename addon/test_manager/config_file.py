
from pathlib import Path

from enum import Enum

class TestMode(Enum):

    BACKGROUND = "background"
    RUNTIME = "runtime"

class ConfigFile:
    '''Reads pyproject.toml file
    
    :param pythonpath: Path to test cwd
    :param test_directory_path: Path to the start search directory for tests
    :param show_log: Show test log
    :param selected_functions: List of selected functions to test functions to run
    :param toggle_console: Toggle console before and after running tests
    :param test_mode: Define the test process mode to be used, background or runtime.
        In background mode, the test is run in a subprocess, in runtime mode, the test is run in
        the current blender process.
    
    '''

    pythonpath : Path
    show_log : bool
    selected_functions : list[Path]
    toggle_console : bool
    test_mode : TestMode

    def __init__(self, source_directory : Path):

        self.source_directory = source_directory

        pyproject_toml_filepath = Path(source_directory, "pyproject.toml")

        if not pyproject_toml_filepath.exists():
            raise Exception("pyproject.toml not found")

        self.load_pyproject_toml()

    def load_pyproject_toml(self):

        import toml # type: ignore

        try:
            pyproject_toml = toml.load(Path(self.source_directory, "pyproject.toml"))["tool"]["bpytest"]
        except KeyError:
            print("tool.bpytest not found")
            return
        
        self.pythonpath = pyproject_toml.get("pythonpath")
        self.show_log = pyproject_toml.get("show_log", False)
        self.selected_functions = pyproject_toml.get("selected_functions", [])
        self.toggle_console = pyproject_toml.get("toggle_console", False)
        self.raise_error = pyproject_toml.get("raise_error",False)
        self.test_mode = TestMode(pyproject_toml.get("test_mode", "background"))