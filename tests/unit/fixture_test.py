from conftest import BPY_TEST_FILES, assert_execute_test_unit


def test_built_in_fixture():
    """Test the built-in fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "fixture_test.py", "test_built_in_fixture"
    )


def test_custom_fixture():
    """Test the custom fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "fixture_test.py", "test_custom_fixture"
    )


def test_blender_object_fixture():
    """Test the custom fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "fixture_test.py", "test_blender_object_fixture"
    )
