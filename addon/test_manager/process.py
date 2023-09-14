import bpy #type:ignore
import subprocess
import importlib.util
import traceback
import sys, os

from pathlib import Path

from abc import ABC, abstractmethod

from . import TestUnit

class OutputHandler:
    def __init__(self, display_output : bool):
        
        self._display_output = display_output
        self.messages = []

    def write(self, message):
        if not message:
            return
        if message == "\n":
            return
        message = message.rstrip()

        if self._display_output: # Allows to display lines without causing a recursion
            print(message, file=sys.__stdout__)

        self.messages.append(message)

    def flush(self):
        pass

def start_output_handler(output_handler : OutputHandler):
    '''Blocks the print function'''
    sys.stdout = output_handler

def stop_output_handler():
    '''Enables the print function'''
    sys.stdout = sys.__stdout__

def overwrite_standard_output(func):
    '''Decorator that overwrites the print function from the sys.__stdout__ to a custom print function'''
    def wrapper(self : TestProcess, *args, **kwargs):

        start_output_handler(self._output_handler)
        result = func(self, *args, **kwargs)
        stop_output_handler()

        self._test_unit.result_lines = self._output_handler.messages
        return result

    return wrapper

class TestProcess(ABC):
    '''Abstract class that defines the test process execution. The execution
    consists in running the test in a subprocess or in the current blender process.

    In the execution of the test, the correct test function is called and the result is 
    returned as a boolean.
    
    :param test_unit: Test unit to be executed
    :param pythonpath: Path python cwd
    :param display_output: Defines if should display the test standard output

    '''

    def __init__(self, test_unit : TestUnit, pythonpath : Path, display_output : bool):

        self._test_unit = test_unit
        self._display_output = display_output
        self._pythonpath = pythonpath

        self._output_handler = OutputHandler(display_output = self._display_output)
    
    @abstractmethod
    def execute(self) -> bool:
        ...

class BackgroundTest(TestProcess):
    '''Runs the test in a subprocess in a different blender process'''

    @overwrite_standard_output
    def execute(self) -> bool:

        generator_filepath = Path(__file__).parent.parent / "generators" /  "background_test_process.py"

        cmd = [
            bpy.app.binary_path,
            "--background",
            "--python", generator_filepath.__str__(),
            "--",
            "filepath:" + self._test_unit.test_file.filepath.__str__(),
            "pythonpath:" + self._pythonpath.__str__(),
            "function_name:" + self._test_unit.function_name
        ]

        result = subprocess.run(
                cmd, 
                check = False, 
                stdout= open(os.devnull, 'w') if not self._display_output else None, 
                stderr= subprocess.PIPE
                )
        
        if result.returncode != 0:
            self._output_handler.messages.append("Error: " + result.stderr.decode("utf-8"))
            return False
        
        return True

class RuntimeTest(TestProcess):
    '''Runs the test in the current blender process'''

    @overwrite_standard_output
    def execute(self):

        module_filepath = self._test_unit.test_file.filepath

        sys.path.append(str(self._pythonpath))

        spec = importlib.util.spec_from_file_location(module_filepath.stem, module_filepath)  
        test_file = importlib.util.module_from_spec(spec) # type:ignore
        spec.loader.exec_module(test_file) # type:ignore
            
        obj = getattr(test_file, self._test_unit.function_name)

        if hasattr(obj, "__call__"): 
            try:
                obj() 
            except:
                traceback.print_exc(file = self._output_handler)
                return False
           
        return True


