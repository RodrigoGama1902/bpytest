import bpytest


@bpytest.fixture
def conftest_fixture():
    """Conftest fixture function."""
    return "conftest_fixture"


@bpytest.fixture(scope="session")
def session_fixture():
    """Session fixture function."""
    return "session_fixture"


@bpytest.fixture(scope="session")
def session_yield_fixture():
    """Session fixture"""

    print("[yield][setup][session_fixture]")
    yield
    print("[yield][teardown][session_fixture]")


@bpytest.fixture(scope="module")
def module_fixture():
    """Module fixture function."""
    return "module_fixture"


@bpytest.fixture(scope="module")
def module_yield_fixture():
    """Module fixture"""

    print("[yield][setup][module_fixture]")
    yield
    print("[yield][teardown][module_fixture]")
