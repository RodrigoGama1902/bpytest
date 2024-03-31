"""Bpy test file with simple tests"""

from pathlib import Path

import bpy

import bpytest


@bpytest.fixture
def custom_fixture():
    """Custom fixture"""
    return "custom_fixture_value"


@bpytest.fixture
def blender_object():
    """Fixture to create a blender object"""
    bpy.ops.mesh.primitive_cube_add()
    return bpy.context.object


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
    assert tmp_path


def test_custom_fixture(custom_fixture: str):
    """Test the custom fixture"""

    print("Test should pass")
    print(custom_fixture)
    assert custom_fixture == "custom_fixture_value"


def test_blender_object_fixture(blender_object: bpy.types.Object):
    """Test the custom fixture"""

    print("Test should pass")
    print(blender_object)
    assert blender_object
