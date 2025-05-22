import argparse
import os
import subprocess
import sys
from pathlib import Path

from common.bpytest_config import BpyTestConfig  # type: ignore[import]
from dotenv import load_dotenv

BLENDER_MODULE_PATH = Path(__file__).parent / "blender_module"


def _call_subprocess(config: BpyTestConfig) -> int:
    """Call the subprocess to execute the test session"""

    if config.blender_exe is None:
        print("Blender executable not found")
        return 1

    generator_filepath = BLENDER_MODULE_PATH / "main.py"

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

    # add no norecursedirs, will be a list for string
    parser.add_argument(
        "-nrd",
        "--norecursedirs",
        nargs="*",
        help="List of directories to be excluded from the test search",
    )

    parser.add_argument(
        "-s", "--nocapture", action="store_true", help="Disable output capture"
    )

    parser.add_argument(
        "-k",
        "--keyword",
        help="Run only tests that match the given keyword expression",
    )

    parser.add_argument(
        "-e",
        "--envfile",
        help="Path to the environment file",
    )

    args = parser.parse_args()
    bpytest_config: BpyTestConfig = BpyTestConfig()

    # ==========================================
    # Handle the environment file
    # ==========================================
    envfile = Path.cwd() / ".env"
    if args.envfile is not None:
        specified_envfile = Path(args.envfile)
        if not specified_envfile.exists():
            print("Specified environment file does not exist")
            sys.exit(1)
        envfile = specified_envfile
    if envfile.exists():
        load_dotenv(envfile.as_posix())
        
    bpytest_config.blender_exe = os.getenv("BLENDER_EXE", None)

    # ==========================================
    # Handle PyProject.toml
    # ==========================================
    pyproject_path = Path.cwd() / "pyproject.toml"
    if pyproject_path.exists():
        bpytest_config.load_from_pyproject_toml(pyproject_path)
        
    # ==========================================
    # Handle Args Input
    # ==========================================
    if args.nocapture is not None:
        bpytest_config.nocapture = args.nocapture
    if args.keyword is not None:
        bpytest_config.keyword = args.keyword
    if args.collector_string is not None:
        bpytest_config.collector_string = args.collector_string
    if args.norecursedirs is not None:
        bpytest_config.norecursedirs = args.norecursedirs
    if args.blender_exe is not None:
        bpytest_config.blender_exe = Path(args.blender_exe)

    if bpytest_config.blender_exe is None:
        print("Blender executable not specified")
        sys.exit(1)
    if not bpytest_config.blender_exe.exists():
        print("Path to blender executable does not exist")
        sys.exit(1)

    sys.exit(_call_subprocess(bpytest_config))


if __name__ == "__main__":
    main()
