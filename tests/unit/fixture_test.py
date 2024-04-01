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


def test_invalid_fixture():
    """Test the invalid fixture, should fail"""

    assert_execute_test_unit(
        False, BPY_TEST_FILES / "fixture_test.py", "test_invalid_fixture"
    )


def test_conftest_fixture():
    """Test the conftest fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "fixture_test.py", "test_conftest_fixture"
    )
