from .entity import CollectorString as CollectorString, TestFile as TestFile
from .print_helper import print_selected_functions as print_selected_functions
from pathlib import Path

IGNORE_DIRS: list[str]

def collect_conftest_files(path: Path, norecursedirs: list[str]) -> list[Path]: ...

class Collector:
    test_files: list[TestFile]
    path: Path
    def __init__(self, collector_string: CollectorString, norecursedirs: list[str], keyword: str = '') -> None: ...
    def get_total_test_units(self, selected_only: bool = False) -> int: ...
    def get_py_files_recursive(self, path: Path, norecursedirs: list[str]) -> list[Path]: ...
