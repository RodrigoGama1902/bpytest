from pathlib import Path

import bpy

import bpytest


@bpytest.fixture
def custom_tmp_path(tmp_path: Path):
    """Custom fixture base don tmp_path built in fixture"""

    custom_basename = "custom_tmp_path"
    custom_path = tmp_path / custom_basename
    if not custom_path.exists():
        custom_path.mkdir()

    return custom_path


def test_tmp_path(tmp_path: Path):
    """Test the built-in fixture, should pass"""
    assert tmp_path.exists()


def test_custom_tmp_path(custom_tmp_path: Path):
    """Test the custom fixture based on tmp_path fixture, should pass"""
    assert custom_tmp_path.exists()


def test_multiple_tmp_path_fixtures(tmp_path: Path, custom_tmp_path: Path):
    """Test multiple tmp_path fixtures, should pass"""
    assert tmp_path.exists()
    assert custom_tmp_path.exists()


def test_save_file(tmp_path: Path):
    """Test the save file in tmp_path, should pass"""
    blend_path = tmp_path / "test.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path.as_posix())
    assert blend_path.exists()
