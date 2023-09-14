import bpy #type:ignore
import subprocess
import importlib.util
import traceback
import sys, os

from pathlib import Path

from abc import ABC, abstractmethod

from . import TestUnit

class PrintCapture:
    def __init__(self, enable_console : bool):
        self._enable_console = enable_console
        self.messages = []

    def write(self, message):
        
        message = message.rstrip().replace("\r", "").replace("\n", "")

        if self._enable_console:
            print(message, file=sys.__stdout__)

        self.messages.append(message)

    def flush(self):
        pass

class TestProcess(ABC):

    def __init__(self, test_unit : TestUnit, pythonpath : Path, show_log : bool):

        self._test_unit = test_unit
        self._show_log = show_log
        self._pythonpath = pythonpath

    @property
    def test_unit(self) -> TestUnit:
        return self._test_unit
    
    @abstractmethod
    def execute(self):
        ...

class BackgroundTest(TestProcess):
    '''Runs the test in a subprocess'''

    def execute(self):

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

        process = subprocess.Popen(cmd, 
                                   universal_newlines=True,
                                   shell=False, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT
                                   )
        
        for line in iter(process.stdout.readline,''): # type: ignore
            if self._show_log:
                print(line.rstrip())

            self.test_unit.log_lines.append(line.rstrip())

        return_code = process.wait()

        if return_code != 0:
            self.test_unit.success = False
        if return_code == 0:    
            self.test_unit.success = True

class RuntimeTest(TestProcess):
    '''Runs the test in the current blender process'''

    def _start_print_handle(self):
        '''Blocks the print function'''
        sys.stdout = self._printer

    @staticmethod
    def _stop_print_handle():
        '''Enables the print function'''
        sys.stdout = sys.__stdout__

    def execute(self):

        self._printer = PrintCapture(enable_console = self._show_log)

        module_filepath = self._test_unit.test_file.filepath

        import sys
        sys.path.append(str(self._pythonpath))

        spec = importlib.util.spec_from_file_location(module_filepath.stem, module_filepath)  
        test_file = importlib.util.module_from_spec(spec) # type:ignore
        spec.loader.exec_module(test_file) # type:ignore
            
        obj = getattr(test_file, self._test_unit.function_name)

        self._start_print_handle()

        if hasattr(obj, "__call__"): 
            try:
                obj() 
            except:
                traceback.print_exc(file = self._printer)
                self._stop_print_handle()

                self.test_unit.success = False
                self.test_unit.log_lines = self._printer.messages
                return
        
        self._stop_print_handle()
        
        self.test_unit.log_lines = self._printer.messages
        self.test_unit.success = True


