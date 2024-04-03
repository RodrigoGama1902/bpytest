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


@bpytest.fixture
def yield_fixture():
    """Yield fixture"""

    print("[yield][setup][yield_fixture]")
    yield
    print("[yield][teardown][yield_fixture]")


@bpytest.fixture
def second_yield_fixture():
    """Second yield fixture"""

    print("[yield][setup][second_yield_fixture]")
    yield
    print("[yield][teardown][second_yield_fixture]")


@bpytest.fixture
def yield_fixture_fixture(yield_fixture: str):
    """Yield fixture with yield fixture"""

    print("[yield][setup][yield_fixture_fixture]")
    yield
    print("[yield][teardown][yield_fixture_fixture]")


@bpytest.fixture
def yield_fixture_fixture_fixture(
    yield_fixture_fixture: str,
):
    """Yield fixture with yield fixture with yield fixture"""

    print("[yield][setup][yield_fixture_fixture_fixture]")
    yield
    print("[yield][teardown][yield_fixture_fixture_fixture]")


def test_built_in_fixture(tmp_path: Path):
    """Test the built-in fixture, should pass"""
    assert tmp_path


def test_custom_fixture(custom_fixture: str):
    """Test the custom fixture, should pass"""
    assert custom_fixture == "custom_fixture_value"


def test_blender_object_fixture(blender_object: bpy.types.Object):
    """Test the custom fixture, should pass"""
    assert blender_object


def test_invalid_fixture(invalid_fixture_name: str):
    """Test the invalid fixture, should fail"""
    assert invalid_fixture_name == "invalid_fixture_value"


def test_conftest_fixture(conftest_fixture: str):
    """Test the conftest fixture, should pass"""
    assert conftest_fixture == "conftest_fixture"


def test_multiple_fixtures(
    custom_fixture: str, blender_object: bpy.types.Object
):
    """Test the multiple fixtures, should pass"""

    assert custom_fixture == "custom_fixture_value"
    assert blender_object


def test_yield_fixture(yield_fixture: str):
    """Test the yield fixture, should pass"""
    print("[yield][test]")


def test_yield_fixture_fixture(
    yield_fixture_fixture: str,
):
    """Test the yield fixture with yield fixture, should pass"""
    print("[yield][test]")


def test_yield_fixture_fixture_fixture(
    yield_fixture_fixture_fixture: str,
):
    """Test the yield fixture with yield fixture with yield fixture, should pass"""
    print("[yield][test]")


def test_multiple_yield_fixtures(
    yield_fixture: str, second_yield_fixture: str
):
    """Test the multiple yield fixtures, should pass"""
    print("[yield][test]")


def test_session_fixture(session_fixture: str):
    """Test the session fixture, should pass"""

    assert session_fixture == "session_fixture"


def test_session_yield_fixture(
    session_yield_fixture: str, yield_fixture_fixture: str
):
    """Test the session yield fixture, should pass"""

    print("[yield][test]")


def test_session_yield_fixture2(
    session_yield_fixture: str, yield_fixture_fixture: str
):
    """Test the session yield fixture, should pass"""

    print("[yield][test]")
