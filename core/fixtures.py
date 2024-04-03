# fixtures.py

import functools
import inspect
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Generator

from .entity import BpyTestConfig, SessionInfo

# Fixture function
FixtureFunction = Callable[..., Any]
# Value returned by a fixture function
FixtureValue = Any | None
# Fixture teardown function callable object
FixtureTeardown = Callable[[], None] | None


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
) -> tuple[FixtureValue, FixtureTeardown]:
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


def inspect_func_for_fixtures(
    func: Callable[..., Any], session_info: SessionInfo, config: BpyTestConfig
) -> tuple[list["FixtureRequest"], list[FixtureValue]]:
    """Inspect a function for fixtures and return the fixture names found."""

    fixture_requests: list["FixtureRequest"] = []
    fixture_values: list[Any] = []

    for arg_name in inspect.getfullargspec(func).args:
        # Skip the iternal request argument since it's already passed
        # when creating the wrapped fixture
        if arg_name == "request":
            continue
        if not arg_name in fixture_manager.fixtures:
            continue

        fixture_request = FixtureRequest(
            func=func,
            fixturename=arg_name,
            session_info=session_info,
            config=config,
        )

        fixture_func, fixture_teardown = fixture_manager.get_fixture(
            arg_name, fixture_request
        )

        fixture_values.append(fixture_func)

        fixture_request.finalizer = fixture_teardown
        fixture_requests.append(fixture_request)

    return fixture_requests, fixture_values


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


class Scope(Enum):
    """Enum class to represent the fixture scope."""

    FUNCTION = auto()
    CLASS = auto()
    MODULE = auto()
    SESSION = auto()


@dataclass
class ModuleValues:
    """Module Values Data class to store the module values."""

    module: Path
    is_module_value_store: bool
    module_value: FixtureValue
    module_teardown: FixtureTeardown


@dataclass
class Fixture:
    """Fixture Data class to store the fixture data."""

    name: str
    func: FixtureFunction
    scope: Scope = field(default=Scope.FUNCTION)

    is_session_value_stored: bool = field(default=False)
    session_value: FixtureValue = field(default=None)
    session_teardown: FixtureTeardown = field(default=None)

    module_values: dict[Path, ModuleValues] = field(default_factory=dict)


class FixtureManager:
    """Fixture Manger class to manage fixtures."""

    fixtures: dict[str, Fixture]

    def __init__(self):
        self.fixtures = {}

    def register_fixture(self, fixture: Fixture):
        """Register a fixture function."""

        for i in self.fixtures:
            if i == fixture.name:
                return

        print(f"Registering fixture: {str(fixture)}")
        self.fixtures[fixture.name] = fixture

    def _create_wrapped_fixture(
        self, original_func: Callable[..., Any], request: FixtureRequest
    ) -> FixtureFunction:
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
    ) -> tuple[FixtureValue, FixtureTeardown]:
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

        fixture: Fixture = self.fixtures[name]
        fixture_agrs: list[FixtureValue] = []

        # Inspect the fixture function for fixtures recursively if there are any
        child_requests, fixture_agrs = inspect_func_for_fixtures(
            fixture.func, request.session_info, request.config
        )

        request.child_requests.extend(child_requests)
        wrapped_fixture_func = self._create_wrapped_fixture(
            fixture.func, request
        )

        # Inject the fixture arguments into the wrapped fixture
        for fixture_arg in fixture_agrs:
            wrapped_fixture_func = functools.partial(
                wrapped_fixture_func, fixture_arg
            )

        return self._get_fixture_value_by_scope(
            fixture, wrapped_fixture_func, request
        )

    @staticmethod
    def _get_fixture_value_by_scope(
        fixture: Fixture,
        wrapped_fixture_func: FixtureFunction,
        request: "FixtureRequest",
    ) -> tuple[FixtureValue, FixtureTeardown]:
        """Get a fixture value by scope and return the value and teardown function."""

        if fixture.scope == Scope.SESSION:
            if not fixture.is_session_value_stored:
                value, teardown = call_fixture_func(
                    wrapped_fixture_func, request, {}
                )
                fixture.session_value = value
                fixture.session_teardown = teardown
                fixture.is_session_value_stored = True

            return fixture.session_value, None

        elif fixture.scope == Scope.MODULE:
            func_module = Path(inspect.getfile(request.func))

            if not fixture.module_values.get(func_module):
                value, teardown = call_fixture_func(
                    wrapped_fixture_func, request, {}
                )

                fixture.module_values[func_module] = ModuleValues(
                    module=func_module,
                    is_module_value_store=True,
                    module_value=value,
                    module_teardown=teardown,
                )
            return (
                fixture.module_values[func_module].module_value,
                None,
            )

        return call_fixture_func(wrapped_fixture_func, request, {})


fixture_manager = FixtureManager()


def fixture(
    func: FixtureFunction | None = None, *, scope: str = "function"
) -> FixtureFunction:
    """Decorator to register a fixture function."""

    def decorator(func: FixtureFunction) -> FixtureFunction:
        fixture_manager.register_fixture(
            Fixture(
                name=func.__name__,
                func=func,
                scope=Scope[scope.upper()] if scope else Scope.FUNCTION,
            )
        )
        return func

    if func is None:
        return decorator
    else:
        return decorator(func)
