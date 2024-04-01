from conftest import BPY_TEST_FILES, assert_execute_test_unit


def test_tmp_path():
    """Test the built-in fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "tmpdir_test.py", "test_tmp_path"
    )


def test_custom_tmp_path():
    """Test the custom fixture based on tmp_path fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "tmpdir_test.py", "test_custom_tmp_path"
    )


def test_multiple_tmp_path_fixtures():
    """Test multiple tmp_path fixtures, should pass"""
    assert_execute_test_unit(
        True,
        BPY_TEST_FILES / "tmpdir_test.py",
        "test_multiple_tmp_path_fixtures",
    )


def test_save_file():
    """Test the save file in tmp_path, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "assertion_test.py", "test_save_file"
    )
