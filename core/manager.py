import importlib.util
import time

from .collector import Collector, collect_conftest_files
from .entity import BpyTestConfig, CollectorString, SessionInfo, TestUnit
from .fixtures import Scope, fixture_manager
from .print_helper import print_failed, print_header
from .runner import TestRunner
from .types import ExitCode


class TestManager:
    """Manages the complete test session"""

    _collector_string: CollectorString
    _collector: Collector
    _finished_tests_list: list[TestUnit]

    _failed: int
    _success: int

    _total_time: float

    def __init__(
        self,
        bpytest_config: BpyTestConfig,
        session_info: SessionInfo,
        collector: Collector,
    ):

        self._finished_tests_list = []
        self._collector = collector
        self._bpytest_config = bpytest_config
        self._session_info = session_info

    @property
    def bpytest_config(self) -> BpyTestConfig:
        return self._bpytest_config

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
        """Computes the result of the test session"""

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
        """Starts the timer to be used to compute the total time of the test session"""
        self.start_time = time.time()

    def _end_time(self):
        """Ends the timer to be used to compute the total time of the test session"""
        self._total_time = time.time() - self.start_time

    def _register_conftest_files(self):
        """Registers the fixtures from conftest files"""

        conftest_files = collect_conftest_files(
            self.bpytest_config.pythonpath, self.bpytest_config.norecursedirs
        )
        for file in conftest_files:
            spec = importlib.util.spec_from_file_location(file.stem, file)
            test_file = importlib.util.module_from_spec(spec)  # type:ignore
            spec.loader.exec_module(test_file)  # type:ignore

    def _finalize_session_fixtures(self):

        for fixture in fixture_manager.fixtures.values():
            if fixture.scope == Scope.SESSION:
                if fixture.session_teardown is not None:
                    fixture.session_teardown()

    def _run_tests(self, collector: Collector):
        """Runs the tests in the collector"""

        self._start_time()

        self._register_conftest_files()

        for test_unit in collector.selected:

            test_process = TestRunner(
                test_unit=test_unit,
                bpytest_config=self._bpytest_config,
                session_info=self._session_info,
            )

            result = test_process.execute()
            test_unit.success = result

            print(test_unit)
            self._finished_tests_list.append(test_unit)

        self._finalize_session_fixtures()
        self._end_time()

    def execute(self) -> ExitCode:
        """Executes the test session"""

        print_header("Test session starts")
        self._run_tests(self._collector)

        print_failed(self._finished_tests_list)
        self._compute_result()

        if self._failed:
            return 1

        return 0
