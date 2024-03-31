"""Singleton class"""

import random
from typing import Any

from .collector import Collector
from .entity import BpyTestConfig, CollectorString, SessionInfo
from .manager import TestManager


def singleton(cls: Any):
    """Singleton decorator"""
    instances = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Session:
    """Singleton class to store the test session id"""

    config: BpyTestConfig
    session_info: SessionInfo

    def __init__(self, config: BpyTestConfig):

        self.config = config
        self.session_info = SessionInfo(id=random.randint(0, 10000))

    def execute(self):
        """Execute the test session"""

        collector = Collector(
            collector_string=CollectorString(self.config.collector_string),
            keyword=self.config.keyword,
        )

        test_manager = TestManager(
            bpytest_config=self.config,
            collector=collector,
            session_info=self.session_info,
        )
        test_manager.execute()


def wrap_session(config: BpyTestConfig):
    """Wrapper function for the test session"""

    session = Session(config)
    session.execute()
