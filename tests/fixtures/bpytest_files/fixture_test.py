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


def test_built_in_fixture(tmp_path: Path):
    """Test the built-in fixture, should pass"""
    assert tmp_path


def test_custom_fixture(custom_fixture: str):
    """Test the custom fixture, should pass"""
    assert custom_fixture == "custom_fixture_value"


def test_blender_object_fixture(blender_object: bpy.types.Object):
    """Test the custom fixture, should pass"""
    assert blender_object
