import fnmatch
import os
from pathlib import Path

from .entity import CollectorString, TestFile, TestUnit
from .print_helper import print_selected_functions

IGNORE_DIRS: list[str] = [
    "__pycache__",
    ".git/*",
    ".vscode/*",
    ".idea/*",
    ".pytest_cache/*",
    "venv/*",
    "build/*",
    "dist/*",
    ".venv/*",
]


def collect_conftest_files(
    path: Path, norecursedirs: list[str] = []
) -> list[Path]:
    """Collect all conftest.py files in the given path."""
    conftest_files = []

    for file_path in path.glob("**/conftest.py"):
        file_name = file_path.name

        # Check if the file path matches any pattern in norecursedirs
        skip_file = False
        for pattern in norecursedirs:
            if fnmatch.fnmatch(
                file_path.relative_to(Path.cwd()).as_posix(), pattern
            ):
                skip_file = True
                break

        if skip_file:
            continue

        if not file_path.is_file():
            continue
        if not file_name.endswith(".py"):
            continue

        conftest_files.append(file_path)

    return conftest_files


class Collector:

    test_files: list[TestFile] = []
    test_units: list[TestUnit] = []
    selected: list[TestUnit] = []

    path: Path

    def __init__(
        self,
        collector_string: CollectorString,
        keyword: str = "",
        norecursedirs: list[str] = [],
    ):

        self._collector_string = collector_string
        norecursedirs.extend(IGNORE_DIRS)

        if self._collector_string.path.is_file():
            self.test_files.append(TestFile(self._collector_string.path))
        if self._collector_string.path.is_dir():
            self.test_files = [
                TestFile(path)
                for path in self.get_py_files_recursive(
                    self._collector_string.path, norecursedirs
                )
            ]

        self.test_units = self._load_all_test_units(self.test_files)

        self.selected = self._filter_by_collector_string(
            self.test_units, self._collector_string
        )

        if keyword:
            self.selected = self.filter_by_keyword(self.selected, keyword)

        print_selected_functions(
            len(self.test_units),
            len(self.test_units) - len(self.selected),
            len(self.selected),
        )

    @staticmethod
    def _load_all_test_units(test_files) -> list[TestUnit]:

        test_units = []

        for test_file in test_files:
            test_units.extend(test_file.test_units)

        return test_units

    @staticmethod
    def _filter_by_collector_string(
        test_units, filter_collector_string: CollectorString
    ) -> list[TestUnit]:

        filtered: list[TestUnit] = []

        for unit in test_units:
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

            filtered.append(unit)

        return filtered

    @staticmethod
    def filter_by_keyword(test_units, keyword):

        functions = []

        for unit in test_units:
            if keyword in unit.function_name:
                functions.append(unit)

        return functions

    def get_py_files_recursive(
        self, path: Path, norecursedirs: list[str] = []
    ):
        py_files = []

        for file_path in path.glob("**/*.py"):
            file_name = file_path.name

            # Check if the file path matches any pattern in norecursedirs
            skip_file = False
            for pattern in norecursedirs:
                if fnmatch.fnmatch(
                    file_path.relative_to(path).as_posix(), pattern
                ):
                    skip_file = True
                    break

            if skip_file:
                continue

            if not "_test.py" in file_name or "test_" in file_name:
                continue
            if not file_path.is_file():
                continue
            if not file_name.endswith(".py"):
                continue

            py_files.append(file_path)

        return py_files
