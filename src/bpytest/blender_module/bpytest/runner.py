import importlib.util
import os
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import bpy
from bpytest_config import BpyTestConfig

from .entity import SessionInfo, TestUnit
from .exception import InvalidFixtureName
from .fixtures import execute_finalize_request, inspect_func_for_fixtures


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
    """Executes the test function and returns the result"""

    sys.path.append(str(pythonpath))

    spec = importlib.util.spec_from_file_location(
        module_filepath.stem, module_filepath
    )
    test_file = importlib.util.module_from_spec(spec)  # type:ignore

    try:
        spec.loader.exec_module(test_file)  # type:ignore
    except ModuleNotFoundError:
        return ExecutionResult(
            False, [f"ModuleNotFoundError: {module_filepath}"]
        )

    obj = getattr(test_file, function_name)

    if hasattr(obj, "__call__"):
        try:
            fixture_requests, args_to_pass = inspect_func_for_fixtures(
                obj, session_info, config
            )
            try:
                result = obj(*args_to_pass)
            except TypeError as e:
                print(str(e))
                raise InvalidFixtureName(function_name) from e

            # Execute fixtures teardown before after the test
            for request in fixture_requests:
                execute_finalize_request(request)

            if result is False:  # Fail if the test returns False
                raise Exception(  # pylint: disable=broad-exception-raised
                    "Test failed, returned False"
                )
            return ExecutionResult(True)
        except:  # pylint: disable=bare-except
            return ExecutionResult(False, [traceback.format_exc()])

    return ExecutionResult(True)


def _enable_module_list(enable_addons: list[str], link_addons: list[str]):
    """Enables the specified modules in the blender environment"""

    enable_addons = enable_addons.copy()

    if link_addons:
        # C:\\Users\\rodri\\AppData\\Roaming\\Blender Foundation\\Blender\\4.1
        blender_data = Path(bpy.utils.resource_path("USER"))
        addons_path = blender_data / "scripts" / "addons"
        if not addons_path.exists():
            os.makedirs(addons_path)

        # link directories to here
        for addon in link_addons:
            addon_path = Path(addon).absolute().resolve()
            if not addon_path.exists():
                print(f"Failed to link addon {addon_path}, it does not exist")
                continue

            addon_link = addons_path / addon_path.name
            if not addon_link.exists():
                os.symlink(addon_path, addon_link, target_is_directory=True)            
            # Add the addon to the enable_addons list
            enable_addons.append(addon_path.name)

    for module in enable_addons:
        bpy.ops.preferences.addon_enable(module=module)
        # if result != {"FINISHED"}:
        #     print(
        #         f"Error enabling module {module.strip()}. "
        #         "Please check if the module is installed."
        #     )
        #     return False


class TestRunner:
    """Test process execution. The execution
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

    def _restore_blender_session(self):
        """Restores the blender session to the default state"""

        bpy.ops.wm.read_factory_settings()

        # Enabling specified modules and bpytest
        enable_addons = self._bpytest_config.enable_addons
        link_addons = self._bpytest_config.link_addons

        _enable_module_list(enable_addons, link_addons)

    def _execute(self):

        self._restore_blender_session()

        execution_result = execute(
            pythonpath=self._pythonpath,
            module_filepath=self._test_unit.test_filepath,
            function_name=self._test_unit.function_name,
            session_info=self._session_info,
            config=self._bpytest_config,
        )

        print(execution_result)

        if not execution_result.success:
            self._test_unit.result_lines = execution_result.result_lines
            return False

        return True
