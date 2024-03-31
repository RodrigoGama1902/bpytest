from conftest import BPY_TEST_FILES, assert_execute_test_unit


def test_tmp_path():
    """Test the tmp_path fixture"""

    assert_execute_test_unit(
        True, BPY_TEST_FILES / "tmpdir_test.py", "test_tmp_path"
    )
