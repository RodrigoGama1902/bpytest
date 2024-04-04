import argparse
import subprocess
import sys
from pathlib import Path

from .entity import BpyTestConfig, RunnerType
from .types import ExitCode


def _call_subprocess(config: BpyTestConfig) -> ExitCode:
    """Call the subprocess to execute the test session"""

    generator_filepath = Path(__file__).parent / "_session_generator.py"

    cmd = [
        config.blender_exe.as_posix(),
        "--background",
        "--factory-startup",
        "--python",
        generator_filepath.as_posix(),
        "--",
        "config=" + config.as_json(),
    ]

    result = subprocess.run(
        cmd,
        check=False,
        stderr=subprocess.PIPE,
    )

    return result.returncode


def main() -> None:
    """Main function"""

    parser = argparse.ArgumentParser(description="Simple test runner")

    # Positional argument for the test file or directory
    parser.add_argument(
        "collector_string",
        nargs="?",
        default=".",
        help="Test file or directory path",
    )

    # Optional arguments
    parser.add_argument(
        "-be",
        "--blender-exe",
        help="Path to blender executable",
    )

    parser.add_argument(
        "-s", "--nocapture", action="store_true", help="Disable output capture"
    )
    parser.add_argument(
        "-k",
        "--keyword",
        help="Run only tests that match the given keyword expression",
    )

    args = parser.parse_args()

    bpytest_config: BpyTestConfig = BpyTestConfig()

    pyproject_path = Path.cwd() / "pyproject.toml"
    if pyproject_path.exists():
        bpytest_config.load_from_pyproject_toml(pyproject_path)

    bpytest_config.runner_type = RunnerType.BACKGROUND
    bpytest_config.nocapture = args.nocapture

    if args.blender_exe is not None:
        bpytest_config.blender_exe = Path(args.blender_exe)
    if args.keyword is not None:
        bpytest_config.keyword = args.keyword
    if args.collector_string is not None:
        bpytest_config.collector_string = args.collector_string

    if bpytest_config.blender_exe is None:
        print("Blender executable not specified")
        sys.exit(1)
    if not bpytest_config.blender_exe.exists():
        print("Path to blender executable does not exist")
        sys.exit(1)

    sys.exit(_call_subprocess(bpytest_config))


if __name__ == "__main__":
    main()
