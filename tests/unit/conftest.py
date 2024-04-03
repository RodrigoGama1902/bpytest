import subprocess
from pathlib import Path

BPY_TEST_FILES = Path("tests/fixtures/bpytest_files")


def assert_execute_test_unit(
    expect_success: bool,
    test_file: Path,
    test_name: str,
    nocapture: bool = False,
) -> tuple[int, list[str]]:
    """Execute a test unit and assert the result"""

    cmd = ["bpytest", f"{test_file}::{test_name}"]
    if nocapture:
        cmd.append("-s")

    return _execute_pytest_command(cmd, expect_success)


def assert_execute_tests_by_keyword(
    expect_success: bool, keyword: str, nocapture: bool = False
) -> tuple[int, list[str]]:
    """Execute tests by keyword and assert the result"""

    cmd = ["bpytest", "-k", keyword]
    if nocapture:
        cmd.append("-s")

    return _execute_pytest_command(cmd, expect_success)


def _execute_pytest_command(
    cmd: list[str], expect_success: bool
) -> tuple[int, list[str]]:

    process = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if expect_success:
        assert process.returncode == 0
    else:
        assert process.returncode != 0

    return process.returncode, process.stdout.splitlines()
