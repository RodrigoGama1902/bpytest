import fnmatch
from pathlib import Path

from .entity import CollectorString, TestFile
from .print_helper import bpyprint, print_selected_functions

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


def collect_conftest_files(path: Path, norecursedirs: list[str]) -> list[Path]:
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
    """Collects test files and test units."""

    test_files: list[TestFile] = []
    path: Path

    def __init__(
        self,
        collector_string: CollectorString,
        norecursedirs: list[str],
        keyword: str = "",
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

        for test_file in self.test_files:
            test_file.select_by_collector_string(self._collector_string)

        if keyword:
            bpyprint(f"Selecting test units by keyword: {keyword}")
            for test_file in self.test_files:
                test_file.select_by_keyword(keyword)

        print_selected_functions(
            self.get_total_test_units(),
            self.get_total_test_units()
            - self.get_total_test_units(selected_only=True),
            self.get_total_test_units(selected_only=True),
        )

    def get_total_test_units(self, selected_only: bool = False) -> int:
        """Get the total number of test units."""

        total = 0
        for test_file in self.test_files:
            if selected_only:
                total += len(
                    [unit for unit in test_file.test_units if unit.selected]
                )
            else:
                total += len(test_file.test_units)
        return total

    def get_py_files_recursive(
        self, path: Path, norecursedirs: list[str]
    ) -> list[Path]:
        """Collect all python files in the given path."""

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
