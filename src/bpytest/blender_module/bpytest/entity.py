from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .print_helper import BColors


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

        color = BColors.OKGREEN.value if self.success else BColors.FAIL.value
        return f'"{self.test_filepath}" {self.function_name} {color} {"[PASSED]" if self.success else "[FAILED]"}{BColors.ENDC.value}'


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
