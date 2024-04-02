from conftest import BPY_TEST_FILES, assert_execute_test_unit


def _check_yield_fixture_output(stdout: list[str], expected: list[str]):

    yield_strings = [
        string for string in stdout if string.startswith("[yield]")
    ]

    assert yield_strings == expected


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

    _check_yield_fixture_output(
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

    _check_yield_fixture_output(
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

    _check_yield_fixture_output(
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

    _check_yield_fixture_output(
        stdout,
        expected=[
            "[yield][setup][yield_fixture]",
            "[yield][setup][second_yield_fixture]",
            "[yield][test]",
            "[yield][teardown][yield_fixture]",
            "[yield][teardown][second_yield_fixture]",
        ],
    )
