import time

from .collector import Collector
from .runner import BackgroundTest, RuntimeTest
from .print_helper import *

from .entity import TestUnit, ConfigFile, TestMode
from pathlib import Path

class TestManager:
    '''Collects, process and manages the test session'''

    _source_directory : Path
    _finished_tests_list : list[TestUnit]

    _failed : int
    _success : int

    _total_time : float

    def __init__(
            self, 
            config_file : ConfigFile,
            collector_string : str = "."):
                
        self._collector_string = collector_string
        self._collector_string_unit = ""
        
        if "::" in self._collector_string:
            self._source_directory = Path(self._collector_string.split("::")[0]).absolute()
            self._collector_string_unit = self._collector_string.split("::")[1]
        else:
            self._source_directory = Path(self._collector_string).absolute()
               
        self._finished_tests_list = []
        self._config_file = config_file
        
        self._pythonpath = Path(self._source_directory, self._config_file.pythonpath).absolute()
        self._test_search_directory = Path(self._source_directory, self._config_file.test_search_relative_path).absolute()

        if not self._source_directory:
            raise Exception("Source Directory not set")
        if not self._test_search_directory.exists():
            raise Exception("Test search directory not found: " + self._test_search_directory.__str__())
    
    @property
    def config_file(self) -> ConfigFile:
        return self._config_file
    
    @property
    def failed(self) -> int:
        return self._failed
    
    @property
    def success(self) -> int:
        return self._success
    
    @property
    def total_time(self) -> float:
        return self._total_time
       
        
    def _compute_result(self):
        '''Computes the result of the test session'''

        self._failed = 0
        self._success = 0

        for test in self._finished_tests_list:
            if not test.success:
                self._failed += 1
            if test.success:
                self._success += 1

        for test in self._finished_tests_list:
            if not test.success:
                print(test)

        print_color = "RED" if self._failed else "GREEN"
        center_text = f"Failed: {self._failed} Success: {self._success} in {self._total_time:.2f} seconds"

        print_header(center_text, print_color)
    
    
    def _start_time(self):
        '''Starts the timer to be used to compute the total time of the test session'''
        self.start_time = time.time()

    def _end_time(self):
        '''Ends the timer to be used to compute the total time of the test session'''
        self._total_time = time.time() - self.start_time

    def _run_tests(self, collector : Collector):
        '''Runs the tests in the collector'''
        
        self._start_time()
        
        
        for test_unit in collector.selected:
            
            match self._config_file.test_mode:
                case TestMode.BACKGROUND:
                    test_class = BackgroundTest
                case TestMode.RUNTIME:
                    test_class = RuntimeTest

            test_process = test_class(
                                    test_unit = test_unit, 
                                    pythonpath = self._pythonpath, 
                                    config_file= self._config_file)
            
            result = test_process.execute()
            test_unit.success = result

            print(test_unit)
            self._finished_tests_list.append(test_unit)
        
        self._end_time()


    def execute(self) -> None:
        '''Executes the test session'''

        print_header("Test session starts")
                
        collector = Collector(self._collector_string)
        
        self._run_tests(collector)

        print_failed(self._finished_tests_list)
        self._compute_result()
