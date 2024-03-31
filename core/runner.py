import importlib.util
import inspect
import os
import subprocess
import sys
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import bpy

from .entity import BpyTestConfig, SessionInfo, TestUnit
from .fixtures import FixtureRequest, fixture_manager


class BlockStandardOutput:
    """Context manager to block the standard output"""

    def __enter__(self):
        self._stdout = (  # pylint: disable=attribute-defined-outside-init
            sys.__stdout__
        )
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Any:
        sys.stdout.close()
        sys.stdout = self._stdout


@dataclass
class ExecutionResult:
    """Class that represents the result of the test execution"""

    success: bool = False
    result_lines: list[str] = field(default_factory=list)


def execute(
    pythonpath: Path,
    module_filepath: Path,
    function_name: str,
    session_info: SessionInfo,
    config: BpyTestConfig,
) -> ExecutionResult:

    sys.path.append(str(pythonpath))

    spec = importlib.util.spec_from_file_location(
        module_filepath.stem, module_filepath
    )
    test_file = importlib.util.module_from_spec(spec)  # type:ignore
    spec.loader.exec_module(test_file)  # type:ignore

    obj = getattr(test_file, function_name)

    if hasattr(obj, "__call__"):
        try:
            func_args = inspect.getfullargspec(obj).args
            args_to_pass: list[Any] = []

            for func_name in func_args:
                if func_name in fixture_manager.fixtures:
                    fixture_request = FixtureRequest(obj, session_info, config)
                    fixture_func = fixture_manager.get_fixture(
                        func_name, fixture_request
                    )
                    args_to_pass.append(fixture_func())

            result = obj(*args_to_pass)
            if result == False:  # Fail if the test returns False
                raise Exception("Test failed, returned False")
            return ExecutionResult(True)
        except:
            return ExecutionResult(False, [traceback.format_exc()])

    return ExecutionResult(True)


class TestRunner(ABC):
    """Abstract class that defines the test process execution. The execution
    consists in running the test in a subprocess or in the current blender process.

    In the execution of the test, the correct test function is called and the result is
    returned as a boolean.

    :param test_unit: Test unit to be executed
    :param pythonpath: Path python cwd
    :param nocapture: Defines if should display the test standard output

    """

    def __init__(
        self,
        test_unit: TestUnit,
        bpytest_config: BpyTestConfig,
        session_info: SessionInfo,
    ):

        self._test_unit = test_unit
        self._bpytest_config = bpytest_config
        self._session_info = session_info
        self._nocapture = bpytest_config.nocapture
        self._pythonpath = bpytest_config.pythonpath

    def execute(self) -> bool:
        """Executes the test and returns the result"""

        if not self._nocapture:
            with BlockStandardOutput():
                result = self._execute()
        else:
            result = self._execute()

        return result

    @abstractmethod
    def _execute(self) -> bool:
        """Executes the test and returns the result"""


class BackgroundTest(TestRunner):
    """Runs the test in a subprocess in a different blender process"""

    def _execute(self) -> bool:

        generator_filepath = (
            Path(__file__).parent / "_runner_blender_script.py"
        )

        cmd = [
            self._bpytest_config.blender_exe.as_posix(),
            "--background",
            "--python",
            generator_filepath.__str__(),
            "--",
            "filepath:" + self._test_unit.test_filepath.__str__(),
            "pythonpath:" + self._pythonpath.__str__(),
            "function_name:" + self._test_unit.function_name,
            "module_list:" + self._bpytest_config.module_list,
        ]

        result = subprocess.run(
            cmd,
            check=False,
            stdout=open(os.devnull, "w") if not self._nocapture else None,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            self._test_unit.result_lines.append(
                "Error: " + result.stderr.decode("utf-8")
            )
            return False

        return True


def _enable_module_list(module_list: list[str]):
    """Enables the specified modules in the blender environment"""

    for module in module_list:
        if module.strip() != "":
            bpy.ops.preferences.addon_enable(module=module.strip())


class RuntimeTest(TestRunner):
    """Runs the test in the current blender process"""

    def _restore_blender_session(self):
        """Restores the blender session to the default state"""

        bpy.ops.wm.read_factory_settings()

        # Enabling specified modules and bpytest
        module_list = self._bpytest_config.module_list.split(",")
        module_list.append("bpytest")

        _enable_module_list(module_list)

    def _execute(self):

        self._restore_blender_session()

        execution_result = execute(
            pythonpath=self._pythonpath,
            module_filepath=self._test_unit.test_filepath,
            function_name=self._test_unit.function_name,
            session_info=self._session_info,
            config=self._bpytest_config,
        )

        if not execution_result.success:
            self._test_unit.result_lines = execution_result.result_lines
            return False

        return True
