"""Singleton class"""

import random

from bpytest_config import BpyTestConfig

from .collector import Collector
from .entity import CollectorString, SessionInfo
from .manager import TestManager
from .types import ExitCode


class Session:
    """Singleton class to store the test session id"""

    config: BpyTestConfig
    session_info: SessionInfo

    def __init__(self, config: BpyTestConfig):

        self.config = config
        self.session_info = SessionInfo(id=random.randint(0, 10000))

    def execute(self) -> ExitCode:
        """Execute the test session"""

        collector = Collector(
            collector_string=CollectorString(self.config.collector_string),
            keyword=self.config.keyword,
            norecursedirs=self.config.norecursedirs,
        )
        test_manager = TestManager(
            bpytest_config=self.config,
            collector=collector,
            session_info=self.session_info,
        )
        return test_manager.execute()


def wrap_session(config: BpyTestConfig) -> ExitCode:
    """Wrapper function for the test session"""

    session = Session(config)
    return session.execute()
