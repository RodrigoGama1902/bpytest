from conftest import BPY_TEST_FILES, assert_execute_test_unit


def test_tmp_path():
    """Test the tmp_path fixture"""

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "tmpdir_test.py", "test_tmp_path"
    )


def test_custom_tmp_path():
    """Test the custom_tmp_path fixture"""

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "tmpdir_test.py", "test_custom_tmp_path"
    )


def test_multiple_tmp_path_fixtures():
    """Test multiple tmp_path fixtures"""

    assert_execute_test_unit(
        True,
        BPY_TEST_FILES / "tmpdir_test.py",
        "test_multiple_tmp_path_fixtures",
    )


def test_save_file():

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_save_file"
    )
