import subprocess
from pathlib import Path

BPY_TEST_FILES = Path("tests/fixtures/bpytest_files")

import os
import shutil

import pytest
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

def _blender_exe() -> str:
    """Fixture to get the Blender executable path."""
    path = os.getenv("BLENDER_EXE", "blender")
    if not shutil.which(path):
        pytest.fail(f"Blender executable not found: {path}")
    return path


def assert_execute_test_unit(
    expect_success: bool,
    test_file: Path,
    test_name: str,
    nocapture: bool = False,
) -> tuple[int, list[str]]:
    """Execute a test unit and assert the result"""

    cmd = ["bpytest",  f"--blender-exe={_blender_exe()}", f"{test_file}::{test_name}"]
    if nocapture:
        cmd.append("-s")

    return _execute_pytest_command(cmd, expect_success)


def assert_execute_tests_by_keyword(
    expect_success: bool, keyword: str, nocapture: bool = False
) -> tuple[int, list[str]]:
    """Execute tests by keyword and assert the result"""

    cmd = ["bpytest", f"--blender-exe={_blender_exe()}", "-k", keyword]
    if nocapture:
        cmd.append("-s")

    return _execute_pytest_command(cmd, expect_success)


def assert_execute_all_tests(
    expect_success: bool, nocapture: bool = False
) -> tuple[int, list[str]]:
    """Execute all tests and assert the result"""

    cmd = ["bpytest", f"--blender-exe={_blender_exe()}"]
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
