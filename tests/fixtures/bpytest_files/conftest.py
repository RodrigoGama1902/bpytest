import bpytest


@bpytest.fixture
def conftest_fixture():
    """Conftest fixture function."""
    return "conftest_fixture"
