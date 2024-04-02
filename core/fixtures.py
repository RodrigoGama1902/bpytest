# fixtures.py

import functools
import inspect
from typing import Any, Callable, Generator

from .entity import BpyTestConfig, SessionInfo

FixtureValue = Callable[..., Any]
FixtureFunction = Callable[..., Any]
FixtureTeardown = Callable[[], None]


def execute_finalize_request(request: "FixtureRequest") -> None:
    """Finalize a fixture request by calling the finalizer of the request
    and all its children requests recursively."""
    if request.finalizer:
        request.finalizer()
    for child_request in request.child_requests:
        execute_finalize_request(child_request)


def call_fixture_func(
    fixturefunc: FixtureFunction,
    request: "FixtureRequest",
    kwargs: dict[str, Any],
) -> tuple[FixtureValue, FixtureTeardown | None]:
    """Call a fixture function and return the result.

    # Note: Based on pytest's implementation
    """

    finalizer = None

    if inspect.isgeneratorfunction(fixturefunc):

        generator = fixturefunc(**kwargs)
        try:
            fixture_result = next(generator)
        except StopIteration:
            raise ValueError(
                f"{request.fixturename} did not yield a value"
            ) from None
        finalizer = functools.partial(
            _teardown_yield_fixture, fixturefunc, generator
        )
    else:
        fixture_result = fixturefunc(**kwargs)

    return fixture_result, finalizer


def _teardown_yield_fixture(
    fixturefunc: FixtureFunction, it: Generator[FixtureValue, None, None]
) -> None:
    """Execute the teardown of a fixture function by advancing the iterator
    after the yield and ensure the iteration ends (if not it means there is
    more than one yield in the function).

    # Note: Based on pytest's implementation
    """
    try:
        next(it)
    except StopIteration:
        pass
    else:
        raise ValueError(
            f"{fixturefunc.__name__} has more than one yield"
        ) from None


class FixtureRequest:
    """Fixture Origin class to store the origin of the fixture."""

    finalizer: functools.partial[Any] | None
    child_requests: list["FixtureRequest"]

    def __init__(
        self,
        func: FixtureFunction,
        fixturename: str,
        session_info: SessionInfo,
        config: BpyTestConfig,
    ):

        self.finalizer = None
        self.child_requests = []

        self.func = func
        self.name = func.__name__
        self.fixturename = fixturename
        self.session_info = session_info
        self.config = config


class FixtureManager:
    """Fixture Manger class to manage fixtures."""

    fixtures: dict[str, Callable[[], Any]]

    def __init__(self):

        self.fixtures = {}

    def register_fixture(self, name: str, fixture_func: Callable[[], Any]):
        """Register a fixture function."""

        print(f"Registering fixture: {name}")
        self.fixtures[name] = fixture_func

    def _create_wrapped_fixture(
        self, original_func: Callable[..., Any], request: FixtureRequest
    ) -> FixtureValue:
        """Create a fixture function with request argument injected."""
        original_params = inspect.signature(original_func).parameters
        if "request" in original_params:
            # If the original function doesn't have a 'request' parameter, add it dynamically
            def wrapper(*args: Any, **kwargs: Any):
                return original_func(*args, **kwargs, request=request)

            return wrapper
        else:
            return original_func

    def get_fixture(
        self, name: str, request: FixtureRequest
    ) -> tuple[FixtureValue, FixtureTeardown | None]:
        """Get a fixture function by name and return a wrapped
        fixture function with internal args injected (Ex: request arg).

        Args:
            name (str): The name of the fixture to get.
            request (FixtureRequest): The origin of the fixture.

        Returns:
            tuple[FixtureValue, FixtureTeardown | None]: The fixture function and the teardown function.
        """

        if name not in self.fixtures:
            raise ValueError(f"Fixture '{name}' not registered.")

        fixture_func = self.fixtures[name]
        fixture_agrs: list[FixtureValue] = []

        # Search for fixtures in the fixture arguments
        for fixture_arg_name in inspect.signature(fixture_func).parameters:
            # Skip the iternal request argument since it's already passed
            # when creating the wrapped fixture
            if fixture_arg_name == "request":
                continue
            if not fixture_arg_name in self.fixtures:
                continue

            fixture_arg_request = FixtureRequest(
                func=fixture_func,
                fixturename=fixture_arg_name,
                session_info=request.session_info,
                config=request.config,
            )

            # recursively get the fixture arguments, and their teardown
            # functions if they have any
            fixture_arg_func, fixture_arg_teardown = self.get_fixture(
                fixture_arg_name, fixture_arg_request
            )

            fixture_agrs.append(fixture_arg_func)

            fixture_arg_request.finalizer = fixture_arg_teardown
            request.child_requests.append(fixture_arg_request)

        wrapped_fixture_func = self._create_wrapped_fixture(
            fixture_func, request
        )

        # Inject the fixture arguments into the wrapped fixture
        for fixture_arg in fixture_agrs:
            wrapped_fixture_func = functools.partial(
                wrapped_fixture_func, fixture_arg
            )

        return call_fixture_func(wrapped_fixture_func, request, {})


fixture_manager = FixtureManager()


def fixture(func: FixtureFunction):
    """Decorator to register a fixture function."""
    fixture_manager.register_fixture(func.__name__, func)
    return func
