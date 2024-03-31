# fixtures.py

import inspect
from typing import Any, Callable

from .session import Session

FixtureValue = Callable[[], Any]
FixtureFunction = Callable[..., Any]


class FixtureRequest:
    """Fixture Origin class to store the origin of the fixture."""

    def __init__(self, func: FixtureFunction, session: Session):
        self.func = func
        self.name = func.__name__
        self.session = session


class FixtureManager:
    """Fixture Manger class to manage fixtures."""

    fixtures: dict[str, Callable[[], Any]]

    def __init__(self):
        self.fixtures = {}

    def register_fixture(self, name: str, fixture_func: Callable[[], Any]):
        """Register a fixture function."""

        self.fixtures[name] = fixture_func

    def _create_fixture(
        self, original_func: Callable[..., Any], request: FixtureRequest
    ) -> FixtureValue:
        """Create a fixture function with internal args."""
        original_params = inspect.signature(original_func).parameters
        if "request" in original_params:
            # If the original function doesn't have a 'request' parameter, add it dynamically
            def wrapper(*args: Any, **kwargs: Any):
                return original_func(*args, **kwargs, request=request)

            return wrapper
        else:
            return original_func

    def get_fixture(self, name: str, request: FixtureRequest) -> FixtureValue:
        """Get a fixture function by name."""

        if name not in self.fixtures:
            raise ValueError(f"Fixture '{name}' not registered.")

        original_func = self.fixtures[name]
        return self._create_fixture(original_func, request)


fixture_manager = FixtureManager()


def fixture(func: FixtureFunction):
    """Decorator to register a fixture function."""
    fixture_manager.register_fixture(func.__name__, func)
    return func
