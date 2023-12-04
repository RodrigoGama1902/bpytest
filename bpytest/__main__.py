import argparse

from .entity import RunnerType, BpyTestConfig, CollectorString
from .manager import TestManager

from .collector import Collector

from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Simple test runner')

    # Positional argument for the test file or directory
    parser.add_argument('collector_string', nargs='?', default='.', help='Test file or directory path')

    # Optional arguments
    parser.add_argument('-s', '--nocapture', action='store_true', help='Disable output capture')
    parser.add_argument('-k', '--keyword', help='Run only tests that match the given keyword expression')
    
    args = parser.parse_args()
    
    collector = Collector(
        collector_string=CollectorString(args.collector_string),
        keyword=args.keyword
    )
    
    bpytest_config = BpyTestConfig()
    bpytest_config.load_from_pyproject_toml(Path.cwd() / 'pyproject.toml')
    
    bpytest_config.runner_type = RunnerType.BACKGROUND
    bpytest_config.nocapture = args.nocapture
    
    test_manager = TestManager(
            bpytest_config = bpytest_config, 
            collector = collector)
    
    test_manager.execute()

if __name__ == "__main__":
    main()