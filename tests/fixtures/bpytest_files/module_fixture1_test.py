"""Module level test file with module level fixtures."""


def test_module_fixture(module_fixture: str):
    """Test the module fixture, should pass"""

    assert module_fixture == "module_fixture"


def test_module_yield_fixture(module_yield_fixture: str):
    """Test the module yield fixture, should pass"""

    print("[yield][test]")


def test_module_yield_fixture2(module_yield_fixture: str):
    """Test the module yield fixture, should pass"""

    print("[yield][test]")
