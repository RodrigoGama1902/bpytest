# fixtures.py

from pathlib import Path
from typing import Any, Callable


class FixtureManager:
    """Fixture Manger class to manage fixtures."""

    fixtures: dict[str, Callable[[], Any]]

    def __init__(self):
        self.fixtures = {}

    def register_fixture(self, name: str, fixture_func: Callable[[], Any]):
        """Register a fixture function."""

        self.fixtures[name] = fixture_func

    def get_fixture(self, name: str):
        """Get a fixture function by name."""

        if name not in self.fixtures:
            raise ValueError(f"Fixture '{name}' not registered.")
        return self.fixtures[name]


fixture_manager = FixtureManager()


def fixture(func: Callable[[], Any]):
    """Decorator to register a fixture function."""
    fixture_manager.register_fixture(func.__name__, func)
    return func


@fixture
def tmp_path() -> Path:
    """Fixture to create a temporary path."""
    return Path()


if __name__ == "__main__":
    # Run tests
    for fixture_name in fixture_manager.fixtures:
        fixture_func = fixture_manager.get_fixture(fixture_name)
        if fixture_func.__name__.startswith("setup"):
            # Run setup fixtures before tests
            fixture_func()

    for test_name in dir():
        if test_name.startswith("test_"):
            # Run tests
            globals()[test_name]()

    for fixture_name in fixture_manager.fixtures:
        fixture_func = fixture_manager.get_fixture(fixture_name)
        if fixture_func.__name__.startswith("teardown"):
            # Run teardown fixtures after tests
            fixture_func()
