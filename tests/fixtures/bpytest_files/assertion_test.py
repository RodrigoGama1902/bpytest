"""Bpy test file with simple tests"""

import bpy


def test_assert_true():
    """Test a assert True, should pass"""
    assert True


def test_return_true():
    """Test a return True, should pass"""
    return True


def test_none_return():
    """Test a return None, should pass"""
    return None


def test_failed():
    """Test a assert False, should fail"""
    assert False


def test_failed_with_false():
    """Test a return False, should fail"""
    return False


def test_failed_with_exception():
    """Test a raise exception, should fail"""
    raise NotImplementedError("Test exception")


def test_cube_creation():
    """Test Blender API calls, should pass"""
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    assert cube
