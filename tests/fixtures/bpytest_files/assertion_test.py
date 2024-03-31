"""Bpy test file with simple tests"""

import bpy


def test_assert_true():
    """Test a simple assert True statement"""
    assert True


def test_return_true():
    """Test a simple return True statement"""
    return True


def test_none_return():
    """Test a simple print statement"""
    return None


def test_failed():
    """Test a failed test"""
    assert False


def test_failed_with_false():
    """Test a failed test with False"""
    return False


def test_failed_with_exception():

    raise NotImplementedError("Test exception")


def test_cube_creation():
    """Test cube creation"""

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    assert cube
