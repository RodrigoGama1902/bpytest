from conftest import BPY_TEST_FILES, assert_execute_test_unit


def test_assert_true():
    """Test a assert True, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_assert_true"
    )


def test_return_true():
    """Test a return True, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_return_true"
    )


def test_none_return():
    """Test a return None, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_none_return"
    )


def test_failed():
    """Test a assert False, should fail"""
    assert_execute_test_unit(
        False, BPY_TEST_FILES / "assertion_test.py", "test_failed"
    )


def test_failed_with_false():
    """Test a return False, should fail"""
    assert_execute_test_unit(
        False, BPY_TEST_FILES / "assertion_test.py", "test_failed_with_false"
    )


def test_failed_with_exception():
    """Test a raise exception, should fail"""
    assert_execute_test_unit(
        False,
        BPY_TEST_FILES / "assertion_test.py",
        "test_failed_with_exception",
    )


def test_cube_creation():
    """Test Blender API calls, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_cube_creation"
    )
