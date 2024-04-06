import functools
from .entity import BpyTestConfig as BpyTestConfig, SessionInfo as SessionInfo
from _typeshed import Incomplete
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

FixtureFunction = Callable[..., Any]
FixtureValue: Incomplete
FixtureTeardown: Incomplete

def execute_finalize_request(request: FixtureRequest) -> None: ...
def call_fixture_func(fixturefunc: FixtureFunction, request: FixtureRequest, kwargs: dict[str, Any]) -> tuple[FixtureValue, FixtureTeardown]: ...
def inspect_func_for_fixtures(func: Callable[..., Any], session_info: SessionInfo, config: BpyTestConfig) -> tuple[list['FixtureRequest'], list[FixtureValue]]: ...

class FixtureRequest:
    finalizer: functools.partial[Any] | None
    child_requests: list['FixtureRequest']
    func: Incomplete
    name: Incomplete
    fixturename: Incomplete
    session_info: Incomplete
    config: Incomplete
    def __init__(self, func: FixtureFunction, fixturename: str, session_info: SessionInfo, config: BpyTestConfig) -> None: ...

class Scope(Enum):
    FUNCTION: Incomplete
    CLASS: Incomplete
    MODULE: Incomplete
    SESSION: Incomplete

@dataclass
class ModuleValues:
    module: Path
    is_module_value_store: bool
    module_value: FixtureValue
    module_teardown: FixtureTeardown
    def __init__(self, module, is_module_value_store, module_value, module_teardown) -> None: ...

@dataclass
class Fixture:
    name: str
    func: FixtureFunction
    module_path: Path
    scope: Scope = ...
    is_session_value_stored: bool = ...
    session_value: FixtureValue = ...
    session_teardown: FixtureTeardown = ...
    module_values: dict[Path, ModuleValues] = ...
    def __init__(self, name, func, module_path, scope, is_session_value_stored, session_value, session_teardown, module_values) -> None: ...

class FixtureManager:
    fixtures: dict[str, Fixture]
    def __init__(self) -> None: ...
    def register_fixture(self, fixture: Fixture): ...
    def get_fixture(self, name: str, request: FixtureRequest) -> tuple[FixtureValue, FixtureTeardown]: ...

fixture_manager: Incomplete

def fixture(func: FixtureFunction | None = None, *, scope: str = 'function') -> FixtureFunction: ...
