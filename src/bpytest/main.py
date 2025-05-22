import argparse
import os
import subprocess
import sys
from pathlib import Path
from pprint import pprint
from typing import Any

import toml
from dotenv import load_dotenv

from .common.bpytest_config import (  # type: ignore[import]
    BpyTestConfig,
    get_bpyconfig_attr_help,
)

BLENDER_MODULE_PATH = Path(__file__).parent / "blender_module"


def _get_blender_exe_list(
    blender_exr_arg: str | None = None,
    blender_exe_id_list: list[str] | None = None,
) -> dict[str, Path]:

    # blender_exe has first priority
    if blender_exr_arg is not None:
        blender_exe = Path(blender_exr_arg)
        if not blender_exe.is_file():
            print(f"--blender_exe arg executable {blender_exe} does not exist")
            sys.exit(1)
        return {"main": blender_exe}

    # If blender_exe_id_list was not specified, use the BLENDER_EXE environment variable
    if not blender_exe_id_list:
        blender_exe = Path(os.getenv("BLENDER_EXE", ""))
        if not blender_exe:
            print(
                (
                    "BLENDER_EXE environment variable not set. "
                    "Alternatively, use the --blender-exe argument."
                )
            )
            sys.exit(1)
        if not blender_exe.is_file():
            print(
                f"Blender executable {blender_exe} from "
                "BLENDER_EXE env variable does not exist"
            )
            sys.exit(1)
        return {"main": blender_exe}

    blender_exe_list = {}
    for blender_exe_id in blender_exe_id_list:
        # Get the environment variable name
        env_var_name = f"BLENDER_{blender_exe_id.upper()}_EXE"
        # Get the value of the environment variable
        blender_exe_path = os.getenv(env_var_name)
        if not blender_exe_path:
            print(
                f"{env_var_name} environment variable not set. cannot find blender executable. "
            )
            sys.exit(1)
        blender_exe = Path(blender_exe_path)
        if not blender_exe.is_file():
            print(
                f"Blender executable {blender_exe} from "
                f"{env_var_name} env variable does not exist"
            )
            sys.exit(1)
        blender_exe_list[blender_exe_id] = blender_exe
        
    if not blender_exe_list:
        print(
            "No blender executable found. "
            "Please set the BLENDER_EXE environment variable or use the --blender-exe argument."
        )
        sys.exit(1)

    return blender_exe_list


def _load_pyproject_toml(pyproject_path: Path) -> dict[str, Any]:
    """Load the pyproject.toml file and return the bpytest section"""

    try:
        return toml.load(pyproject_path)["tool"]["bpytest"]
    except KeyError as exc:
        raise KeyError(
            "tool.bpytest not found in pyproject.toml. "
            "Please make sure the file is in the correct format."
        ) from exc


def _call_subprocess(blender_exe: Path, config: BpyTestConfig, instance_id : str) -> int:
    """Call the subprocess to execute the test session"""

    generator_filepath = BLENDER_MODULE_PATH / "main.py"

    cmd = [
        blender_exe.as_posix(),
        "--background",
        "--factory-startup",
        "--python",
        generator_filepath.as_posix(),
        "--",
        "instance_id=" + instance_id,
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
        help=get_bpyconfig_attr_help("collector_string"),
    )

    parser.add_argument(
        "-be", "--blender-exe", help=get_bpyconfig_attr_help("blender_exe")
    )

    parser.add_argument(
        "-bel",
        "--blender-exe-id-list",
        help=(
            "List of blender executable ids to be used for the test session, "
            "each specified ID will be used to find the corresponding env variable with the path to the blender executable. "
            "e.g. 'blender_3_5' will look for the env variable 'BLENDER_3_5' and use its value as the path to the blender executable. "
            "This is useful for testing multiple versions of blender in the same test session."
        ),
    )

    # add no norecursedirs, will be a list for string
    parser.add_argument(
        "-nrd",
        "--norecursedirs",
        nargs="*",
        help=get_bpyconfig_attr_help("norecursedirs"),
    )

    parser.add_argument(
        "-s",
        "--nocapture",
        action="store_true",
        help=get_bpyconfig_attr_help("nocapture"),
    )

    parser.add_argument(
        "-k",
        "--keyword",
        help=get_bpyconfig_attr_help("keyword"),
    )

    parser.add_argument(
        "-e",
        "--envfile",
        help="Path to the environment file",
    )

    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show the current configuration and exit",
    )

    args = parser.parse_args()

    # ==============================================================
    # Load Environment Variables from .env file if it exists
    # ==============================================================
    envfile = Path.cwd() / ".env"
    if args.envfile is not None:
        specified_envfile = Path(args.envfile)
        if not specified_envfile.exists():
            print("Specified environment file does not exist")
            sys.exit(1)
        envfile = specified_envfile
    if envfile.exists():
        load_dotenv(envfile.as_posix())

    # ==============================================================
    # Handle PyProject.toml
    # ==============================================================
    pyproject_path = Path.cwd() / "pyproject.toml"
    pyproject_data = {}
    if pyproject_path.exists():
        pyproject_data = _load_pyproject_toml(pyproject_path)

    # ==============================================================
    # Create the BpyTestConfig object
    # ==============================================================
    bpytest_config: BpyTestConfig = BpyTestConfig()

    # Populate the config with the data from the pyproject.toml file
    if pyproject_data:
        bpytest_config.load_from_pyproject_data(pyproject_data)

    # Populate the config with the data from the command line arguments
    # (Can override the data from the pyproject.toml file)
    if args.nocapture is not None:
        bpytest_config.nocapture = args.nocapture
    if args.keyword is not None:
        bpytest_config.keyword = args.keyword
    if args.collector_string is not None:
        bpytest_config.collector_string = args.collector_string
    if args.norecursedirs is not None:
        bpytest_config.norecursedirs = args.norecursedirs
    if args.show_config:
        print("Current configuration:")
        pprint(bpytest_config.__dict__)
        sys.exit(0)

    # ==============================================================
    # Get blender executable instances to run the tests
    # ==============================================================
    blender_exe_id_list = []
    if pyproject_data.get("blender_exe_id_list", []):
        blender_exe_id_list = pyproject_data.get("blender_exe_id_list", [])
    if args.blender_exe_id_list is not None:
        blender_exe_id_list = args.blender_exe_id_list.split(",")
    blender_exe_list = _get_blender_exe_list(
        blender_exr_arg=args.blender_exe,
        blender_exe_id_list=blender_exe_id_list,
    )

    return_codes = []
    for instance_id, blender_exe in blender_exe_list.items():
        return_code = _call_subprocess(blender_exe, bpytest_config, instance_id)
        return_codes.append(return_code)
        
    if any(code != 0 for code in return_codes):
        sys.exit(1)
        
    sys.exit(0)

if __name__ == "__main__":
    main()
