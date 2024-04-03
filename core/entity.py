import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from colorama import Fore


class RunnerType(Enum):

    BACKGROUND = "background"
    RUNTIME = "runtime"


class CollectorString:

    collector_string: str
    unit: str = ""
    directory: Path
    path: Path

    def __init__(self, collector_string: str):

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
class SessionInfo:

    id: int


@dataclass
class BpyTestConfig:
    """Class that represents the configuration of the test session.

    :param pythonpath: Path python cwd
    :param nocapture: Show test log
    :param toggle_console: Toggle console before and after running tests
    :param runner_type: Define the test process mode to be used, background or runtime.
        In background mode, the test is run in a subprocess, in runtime mode, the test is run in
        the current blender process.
    :param module_list: List of modules to be loaded before running the tests
    :param blender_exe: Path to blender executable

    """

    pythonpath: Path = field(default=Path.cwd())
    nocapture: bool = field(default=False)
    toggle_console: bool = field(default=False)
    module_list: str = field(default="")
    runner_type: RunnerType = field(default=RunnerType.BACKGROUND)
    blender_exe: Path = field(default=Path.cwd())
    norecursedirs: list[str] = field(default_factory=list)

    collector_string: str = field(default="")
    keyword: str = field(default="")

    def load_from_dict(self, data: dict[str, Any]):
        """Loads the config from a dict"""
        for key, value in data.items():

            if value == "True":
                setattr(self, key, True)
            elif value == "False":
                setattr(self, key, False)
            elif value == "None":
                setattr(self, key, None)
            elif value.startswith("[") and value.endswith("]"):
                value = value[1:-1].split(",")
                for idx, i in enumerate(value):
                    value[idx] = i.replace("'", "").strip()
                setattr(self, key, value)
            elif hasattr(self, key):
                field_type = getattr(
                    self.__dataclass_fields__[key], "type", None
                )
                if field_type is not None:
                    # Handle special cases, such as Path
                    if field_type == Path:
                        setattr(self, key, Path(value))
                    else:
                        setattr(self, key, field_type(value))
                else:
                    setattr(self, key, value)

    def load_from_pyproject_toml(self, pyproject_toml_path: Path):
        """Loads the config file from pyproject.toml"""

        import toml  # type: ignore

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
        self.raise_error = pyproject_toml.get("raise_error", False)
        self.module_list = pyproject_toml.get("module_list", "")
        self.norecursedirs = pyproject_toml.get("norecursedirs", [])
        self.runner_type = RunnerType(
            pyproject_toml.get("runner_type", "background")
        )
        self.blender_exe = Path(pyproject_toml.get("blender_exe", Path.cwd()))

    def as_dict(self) -> dict[str, Any]:
        """Returns the config as a json"""

        json_data: dict[str, Any] = {}

        for key, value in self.__dict__.items():
            # check if is enum
            if hasattr(value, "value"):
                json_data[key] = value.value
            else:
                json_data[key] = str(value)

        return json_data

    def as_json(self) -> str:
        """Returns the config as a json"""

        return json.dumps(self.as_dict())


class TestUnit:

    function_name: str
    success: bool
    test_filepath: Path
    result_lines: list[str]
    collector_string: CollectorString
    selected: bool

    def __init__(self, test_filepath: Path, function_name: str):

        self.result_lines = []
        self.test_filepath = test_filepath
        self.function_name = function_name
        self.collector_string = CollectorString(
            f"{self.test_filepath}::{self.function_name}"
        )

        self.selected = False
        self.success = False

    def print_log(self):
        for line in self.result_lines:
            print(line)

    def __repr__(self) -> str:

        color = Fore.GREEN if self.success else Fore.RED
        return f'"{self.test_filepath}" {self.function_name} {color} {"[PASSED]" if self.success else "[FAILED]"}{Fore.RESET}'


class TestFile:
    """Class that represents a test file"""

    filepath: Path
    test_units: list[TestUnit]

    def __init__(self, filepath: Path):

        self.filepath = filepath
        self.test_units = self._parse_test_units()

    def _parse_test_units(self) -> list[TestUnit]:
        """# TODO: The test unit collection method should be by
        importlib.util"""

        test_units = []

        with open(self.filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if not "def test_" in line:
                    continue

                function_name = line.split("def ")[1].split("(")[0]
                test_units.append(TestUnit(self.filepath, function_name))

        return test_units

    def select_by_collector_string(
        self, filter_collector_string: CollectorString
    ) -> None:
        """Selects test units by collector string"""

        for unit in self.test_units:
            if filter_collector_string.path.is_file():
                if (
                    not filter_collector_string.path
                    == unit.collector_string.path
                ):
                    continue
            if filter_collector_string.path.is_dir():
                if not unit.collector_string.path.is_relative_to(
                    filter_collector_string.path
                ):
                    continue
            if filter_collector_string.unit:
                if (
                    not filter_collector_string.unit
                    == unit.collector_string.unit
                ):
                    continue

            unit.selected = True

    def select_by_keyword(self, keyword: str) -> None:
        """Selects test units by keyword"""

        for unit in self.test_units:
            if not keyword in unit.function_name:
                unit.selected = False
