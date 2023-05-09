import bpy

import os
import subprocess
import sys

from pathlib import Path

class TestFile:

    selected_functions : list[str] = []
    filepath : Path
    
    def __init__(self, filepath, selected_functions = []):

        self.filepath = filepath
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

        test_function_names = self.parse_test_function_names()

        for function_name in test_function_names:
            if not selected_functions:
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

    log_lines : list[str] = []

    def __init__(self, test_file : TestFile, function_name : str):
        self.test_file = test_file
        self.function_name = function_name
        self.success = False
    
    def print_log(self):
        for line in self.log_lines:
            print(line)
    
    def __repr__(self) -> str:
        return f'"{self.test_file.filepath}" {self.function_name} {"[Success]" if self.success else "[Failed]"}'

class Collector:

    test_files : list[TestFile] = []
    path : Path
    
    def __init__(self, path, selected_functions = []):
        self.path = path
 
        if path.is_file():
            self.test_files.append(TestFile(path, selected_functions))
        if path.is_dir():
            self.test_files = [TestFile(path, selected_functions) for path in self.get_py_files_recursive(path)]

    def get_py_files_recursive(self, path):

        py_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                
                if not file.endswith(".py"):
                    continue
                if not "_test.py" in file or "test_" in file:
                    continue

                py_files.append(Path(root, file))

        return py_files

class TestProcess:

    def __init__(self, test_unit : TestUnit, pythonpath : Path, show_log : bool):

        self.test_unit = test_unit
        self.show_log = show_log

        generator_filepath = Path(__file__).parent.joinpath("generator.py")

        self.cmd = [
            bpy.app.binary_path,
            "--background",
            "--python", generator_filepath.__str__(),
            "--",
            "filepath:" + test_unit.test_file.filepath.__str__(),
            "pythonpath:" + pythonpath.__str__(),
            "function_name:" + test_unit.function_name
        ]

    def execute(self):

        process = subprocess.Popen(self.cmd, 
                                   universal_newlines=True,
                                   shell=True, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT
                                   )
        
        for line in iter(process.stdout.readline,''): # type: ignore
            if self.show_log:
                print(line.rstrip())

            self.test_unit.log_lines.append(line.rstrip())

        return_code = process.wait()

        if return_code != 0:
            self.test_unit.success = False
        if return_code == 0:    
            self.test_unit.success = True

class ConfigFile:

    pythonpath : Path
    test_directory_path : Path
    show_log : bool
    selected_functions : list[Path]
    toggle_console : bool

    def __init__(self, source_directory : Path):

        self.source_directory = source_directory

        pyproject_toml_filepath = Path(source_directory, "pyproject.toml")
        if pyproject_toml_filepath.exists():
            self.load_pyproject_toml()
            return 

    def load_pyproject_toml(self):

        import toml # type: ignore

        try:
            pyproject_toml = toml.load(Path(self.source_directory, "pyproject.toml"))["tool"]["bpytest"]
        except KeyError:
            print("tool.bpytest not found")
            return
        
        self.pythonpath = pyproject_toml.get("pythonpath")
        self.test_directory_path = pyproject_toml.get("test_directory_path", "")
        self.show_log = pyproject_toml.get("show_log", False)
        self.selected_functions = pyproject_toml.get("selected_functions", [])
        self.toggle_console = pyproject_toml.get("toggle_console", False)
        self.raise_error = pyproject_toml.get("raise_error",False)

class BPYTEST_OT_Tests(bpy.types.Operator):
    """Run Tests"""

    bl_idname = "bpytest.run_tests"
    bl_label = "Delete Job"
    bl_options = {'REGISTER', 'UNDO'}
    
    source_directory : bpy.props.StringProperty(name = 'Addon Source Directory', 
                                                description = "Addon Source Directory",
                                                ) # type:ignore
    
    _tests_list : list[TestUnit]

    def _print_failed(self):

        for test in self._tests_list:
            if not test.success:
                print("----------------------------------------------------------------------")
                test.print_log()
    
    def _compute_result(self):

        self._failed = 0
        self._success = 0

        for test in self._tests_list:
            if not test.success:
                self._failed += 1
            if test.success:
                self._success += 1

        print("----------------------------------------------------------------------")
        for test in self._tests_list:
            if not test.success:
                print(test)
        print("----------------------------------------------------------------------")
        print(f"Failed: {self._failed} Success: {self._success}")
        print("----------------------------------------------------------------------")

    def execute(self, context):

        if not self.source_directory:
            self.report({'ERROR'}, "Source Directory not set")
            return {'FINISHED'}

        config_file = ConfigFile(Path(self.source_directory))

        if config_file.toggle_console:
            bpy.ops.wm.console_toggle()

        self._tests_list = []

        self.pythonpath = Path(self.source_directory, config_file.pythonpath).absolute()
        test_path = Path(self.pythonpath, config_file.test_directory_path).absolute()

        sys.path.append(str(test_path))

        if not test_path.exists():
            self.report({'ERROR'}, "Test path not found: " + test_path.__str__())
            return {'FINISHED'}
        
        print("Running tests from: " + test_path.__str__() + "\n")
        collector = Collector(test_path, config_file.selected_functions)
        
        for test_file in collector.test_files:
            for function_name in test_file.selected_functions:
                test_unit = TestUnit(test_file, function_name)

                test_process = TestProcess(test_unit = test_unit, 
                                           pythonpath = self.pythonpath, 
                                           show_log = config_file.show_log)
                test_process.execute()

                print(test_process.test_unit)
                self._tests_list.append(test_unit)

        self._print_failed()
        self._compute_result()

        if self._failed:
            if config_file.raise_error:
                raise Exception("Tests Failed")

        if config_file.toggle_console:
            bpy.ops.wm.console_toggle()
 
        return {'FINISHED'}


