from conftest import BPY_TEST_FILES, assert_execute_test_unit


def test_assert_true():
    """Test a simple assert True statement"""

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_assert_true"
    )


def test_return_true():

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_return_true"
    )


def test_none_return():
    """Test a simple print statement"""

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_none_return"
    )


def test_failed():

    assert_execute_test_unit(
        False, BPY_TEST_FILES / "assertion_test.py", "test_failed"
    )


def test_failed_with_false():

    assert_execute_test_unit(
        False, BPY_TEST_FILES / "assertion_test.py", "test_failed_with_false"
    )


def test_failed_with_exception():

    assert_execute_test_unit(
        False,
        BPY_TEST_FILES / "assertion_test.py",
        "test_failed_with_exception",
    )


def test_cube_creation():

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_cube_creation"
    )
