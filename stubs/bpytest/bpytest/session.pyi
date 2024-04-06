from .collector import Collector as Collector
from .entity import BpyTestConfig as BpyTestConfig, CollectorString as CollectorString, SessionInfo as SessionInfo
from .manager import TestManager as TestManager
from .types import ExitCode as ExitCode

class Session:
    config: BpyTestConfig
    session_info: SessionInfo
    def __init__(self, config: BpyTestConfig) -> None: ...
    def execute(self) -> ExitCode: ...

def wrap_session(config: BpyTestConfig) -> ExitCode: ...
