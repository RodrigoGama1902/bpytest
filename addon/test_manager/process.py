import bpy #type:ignore
import subprocess
import importlib.util
import traceback
import sys, os

from pathlib import Path

from abc import ABC, abstractmethod

from . import TestUnit
from . import ConfigFile


class TestProcess(ABC):
    '''Abstract class that defines the test process execution. The execution
    consists in running the test in a subprocess or in the current blender process.

    In the execution of the test, the correct test function is called and the result is 
    returned as a boolean.
    
    :param test_unit: Test unit to be executed
    :param pythonpath: Path python cwd
    :param display_output: Defines if should display the test standard output

    '''

    def __init__(self, test_unit : TestUnit, pythonpath : Path, config_file : ConfigFile):

        self._test_unit = test_unit
        self._config_file = config_file
        self._display_output = config_file.display_output
        self._pythonpath = pythonpath

    def _block_standard_output(self):
        '''Blocks the print function if display_output is False'''
        if not self._display_output:
            sys.stdout = open(os.devnull, 'w')

    def _restore_standard_output(self):
        '''Enables the print function if display_output is False'''

        if not self._display_output:
            sys.stdout = sys.__stdout__

    def execute(self) -> bool:
        '''Executes the test and returns the result'''
        
        self._block_standard_output()
        result = self._execute()
        self._restore_standard_output()
        
        return result

    @abstractmethod
    def _execute(self) -> bool:
        '''Executes the test and returns the result'''

class BackgroundTest(TestProcess):
    '''Runs the test in a subprocess in a different blender process'''

    def _execute(self) -> bool:

        generator_filepath = Path(__file__).parent.parent / "generators" /  "background_test_process.py"

        cmd = [
            bpy.app.binary_path,
            "--background",
            "--python", generator_filepath.__str__(),
            "--",
            "filepath:" + self._test_unit.test_file.filepath.__str__(),
            "pythonpath:" + self._pythonpath.__str__(),
            "function_name:" + self._test_unit.function_name,
            "module_list:" + self._config_file.module_list
        ]

        result = subprocess.run(
                cmd, 
                check = False, 
                stdout= open(os.devnull, 'w') if not self._display_output else None, 
                stderr= subprocess.PIPE
                )
        
        if result.returncode != 0:
            self._test_unit.result_lines.append("Error: " + result.stderr.decode("utf-8"))
            return False
        
        return True

class RuntimeTest(TestProcess):
    '''Runs the test in the current blender process'''

    def _execute(self):

        module_filepath = self._test_unit.test_file.filepath

        sys.path.append(str(self._pythonpath))

        spec = importlib.util.spec_from_file_location(module_filepath.stem, module_filepath)  
        test_file = importlib.util.module_from_spec(spec) # type:ignore
        spec.loader.exec_module(test_file) # type:ignore
            
        obj = getattr(test_file, self._test_unit.function_name)

        if hasattr(obj, "__call__"): 
            try:
                result = obj() 
                if result == False: # Fail if the test returns False
                   raise Exception("Test failed, returned False")
                return True
            except:
                self._test_unit.result_lines.append(traceback.format_exc())
                return False
           
        return True


