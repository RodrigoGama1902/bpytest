from conftest import (
    BPY_TEST_FILES,
    assert_execute_all_tests,
    assert_execute_test_unit,
    assert_execute_tests_by_keyword,
)


def _check_yield_fixture_output_by_value_order(
    stdout: list[str], expected: list[str]
):

    yield_strings = [
        string for string in stdout if string.startswith("[yield]")
    ]

    assert yield_strings == expected


def _check_yield_fixture_output_by_count(
    stdout: list[str], value: str, count: int
):

    yield_strings = [string for string in stdout if string == value]
    assert len(yield_strings) == count


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


def test_yield_fixture():
    """Test the yield fixture, should pass"""

    _, stdout = assert_execute_test_unit(
        True,
        BPY_TEST_FILES / "fixture_test.py",
        "test_yield_fixture",
        nocapture=True,
    )

    _check_yield_fixture_output_by_value_order(
        stdout,
        expected=[
            "[yield][setup][yield_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture]",
        ],
    )


def test_yield_fixture_fixture():
    """Test the yield fixture with yield fixture, should pass"""

    _, stdout = assert_execute_test_unit(
        True,
        BPY_TEST_FILES / "fixture_test.py",
        "test_yield_fixture_fixture",
        nocapture=True,
    )

    _check_yield_fixture_output_by_value_order(
        stdout,
        expected=[
            "[yield][setup][yield_fixture]",
            "[yield][setup][yield_fixture_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture_fixture]",
            "[yield][teardown][yield_fixture]",
        ],
    )


def test_yield_fixture_fixture_fixture():
    """Test the yield fixture with yield fixture with yield fixture, should pass"""

    _, stdout = assert_execute_test_unit(
        True,
        BPY_TEST_FILES / "fixture_test.py",
        "test_yield_fixture_fixture_fixture",
        nocapture=True,
    )

    _check_yield_fixture_output_by_value_order(
        stdout,
        expected=[
            "[yield][setup][yield_fixture]",
            "[yield][setup][yield_fixture_fixture]",
            "[yield][setup][yield_fixture_fixture_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture_fixture_fixture]",
            "[yield][teardown][yield_fixture_fixture]",
            "[yield][teardown][yield_fixture]",
        ],
    )


def test_multiple_yield_fixtures():
    """Test the multiple yield fixtures, should pass"""

    _, stdout = assert_execute_test_unit(
        True,
        BPY_TEST_FILES / "fixture_test.py",
        "test_multiple_yield_fixtures",
        nocapture=True,
    )

    _check_yield_fixture_output_by_value_order(
        stdout,
        expected=[
            "[yield][setup][yield_fixture]",
            "[yield][setup][second_yield_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture]",
            "[yield][teardown][second_yield_fixture]",
        ],
    )


def test_session_fixture():
    """Test the session fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "fixture_test.py", "test_session_fixture"
    )


def test_session_yield_fixture():
    """Test the session yield fixture, should pass"""

    _, stdout = assert_execute_tests_by_keyword(
        True, "test_session_yield_fixture", nocapture=True
    )

    _check_yield_fixture_output_by_value_order(
        stdout,
        expected=[
            "[yield][setup][session_fixture]",
            "[yield][setup][yield_fixture]",
            "[yield][setup][yield_fixture_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture_fixture]",
            "[yield][teardown][yield_fixture]",
            "[yield][setup][yield_fixture]",
            "[yield][setup][yield_fixture_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture_fixture]",
            "[yield][teardown][yield_fixture]",
            "[yield][teardown][session_fixture]",
        ],
    )


def test_module_fixture():
    """Test the module fixture, should pass"""
    assert_execute_test_unit(
        True, BPY_TEST_FILES / "fixture_test.py", "test_module_fixture"
    )


def test_module_yield_fixture():
    """Test the module yield fixture, should pass"""

    _, stdout = assert_execute_tests_by_keyword(
        True, "test_module_yield_fixture", nocapture=True
    )

    _check_yield_fixture_output_by_value_order(
        stdout,
        expected=[
            "[yield][setup][module_fixture]",
            "[yield][test]",
            "[yield][test]",
            "[yield][teardown][module_fixture]",
            "[yield][setup][module_fixture]",
            "[yield][test]",
            "[yield][test]",
            "[yield][teardown][module_fixture]",
        ],
    )


def test_all_fixtures_setup_and_teardown():
    """Assert that the all fixtures are setup and teardown correctly"""

    _, stdout = assert_execute_all_tests(False, nocapture=True)

    # Only one session fixture should be setup and teardown
    _check_yield_fixture_output_by_count(
        stdout, "[yield][setup][session_fixture]", 1
    )
    _check_yield_fixture_output_by_count(
        stdout, "[yield][teardown][session_fixture]", 1
    )

    # Only Two module fixtures should be setup and teardown
    # (since there are two module files that requests the module fixture)
    _check_yield_fixture_output_by_count(
        stdout, "[yield][setup][module_fixture]", 2
    )
    _check_yield_fixture_output_by_count(
        stdout, "[yield][teardown][module_fixture]", 2
    )
