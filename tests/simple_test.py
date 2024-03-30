from pathlib import Path

import bpy  # type:ignore

from bpytest.bpytest.fixtures import fixture


@fixture
def custom_fixture():
    """Custom fixture"""
    return "custom_fixture_value"


def test_simple_print():
    """Test a simple print statement"""
    print("Test should pass")


def test_failed():
    """Test a failed test"""
    print("Test Should fail")
    assert False


def test_failed_with_false():
    """Test a failed test with False"""
    print("Test Should fail")
    return False


def test_cube_creation():
    """Test cube creation"""
    print("Test should pass")

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    assert cube


def test_built_in_fixture(tmp_path: Path):
    """Test the built-in fixture"""

    print("Test should pass")
    print(tmp_path.absolute())
    assert tmp_path


def test_custom_fixture(custom_fixture: str):
    """Test the custom fixture"""

    print("Test should pass")
    print(custom_fixture)
    assert custom_fixture == "custom_fixture_value"
