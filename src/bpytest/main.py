import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from pprint import pprint
from typing import Any

import toml
from dotenv import load_dotenv

from .common.bpyprint import decode_bpyprint, is_bpyprint  # type: ignore[import]
from .common.bpytest_config import (  # type: ignore[import]
    BpyTestConfig,
    ConfigFileBlenderLevel,
    ConfigFilePackageLevel,
    SessionConfig,
)

BLENDER_MODULE_PATH = Path(__file__).parent / "blender_module"

def _print_config_file_help() -> None:
    """Print the help for the config file"""

    print("================================================================")
    print("Config file help (pyproject.toml):")
    print("================================================================\n")

    print(ConfigFileBlenderLevel.help())
    print(ConfigFilePackageLevel.help())


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


def _isolate_blender_installation(blender_exe: Path) -> tuple[Path, Path]:
    """Create a temporary directory to isolate the blender installation and a portable directory
    This is used to avoid conflicts with the user configuration files and add-ons from the original installation

    Returns:
        tuple[Path, Path]: a tuple containing
            - the path to the temporary directory
            - the path to the blender executable in the temporary directory
    """
    # ============================================================
    # Clone the blender installation to a temporary directory
    # ============================================================
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Isolating blender installation {blender_exe} at {temp_dir} ")
    shutil.copytree(blender_exe.parent, temp_dir, dirs_exist_ok=True)

    blender_bin_name = (
        "blender.exe" if platform.system() == "Windows" else "blender"
    )
    # ============================================================
    # Create portable directory
    # ============================================================
    # https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html
    #
    # NOTE: On Blender 4.2 and above, if a 'portable' directory is created,
    # blender will use it to store the user configuration files, including
    # Add-ons. On Blender versions below 4.2, this directory is ignored.
    #
    # Only supported on Windows and Linux, on MacOS, it works another way
    # but will not be implemented for now.

    portable_dir = temp_dir / "portable"
    portable_dir.mkdir(parents=True, exist_ok=True)

    return temp_dir, temp_dir / blender_bin_name


def _install_python_dependencies(
    blender_exe: Path, python_dependencies: list[str]
) -> None:
    """Install python dependencies"""

    # Depending on the blender version, the python executable is located in different folders
    # e.g:
    # 3.5: blender_exe.parent\3.5\python\bin\python.exe
    # 3.6: blender_exe.parent\3.6\python\bin\python.exe
    # 4.4: blender_exe.parent\4.4\python\bin\python.exe
    #
    # Here we are testing different folders in the blender_exe.parent dir
    # to find the python executable
    python_bin_path: Path | None = None
    _python_bin_name = (
        "python.exe" if platform.system() == "Windows" else "python3"
    )
    for folder in blender_exe.parent.iterdir():
        _python_bin_path = folder / "python" / "bin" / _python_bin_name
        if _python_bin_path.is_file():
            python_bin_path = _python_bin_path
            break
    if python_bin_path is None:
        raise RuntimeError(
            f"Could not find python executable in {blender_exe.parents}. "
            "Please make sure the blender executable is in the correct format."
        )

    # Install pip if not already installed
    try:
        subprocess.run([python_bin_path, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip

        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)

    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"
    environ_copy["PIP_NO_CACHE_DIR"] = "1"

    for dep in python_dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run(
                [
                    python_bin_path,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    dep,
                ],
                check=True,
                env=environ_copy,
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {dep}: {e}")
            raise e


def _call_subprocess(
    blender_exe: Path, config: BpyTestConfig, instance_id: str
) -> int:
    """Call the subprocess to execute the test session, streaming its output."""

    generator_filepath = BLENDER_MODULE_PATH / "main.py"

    cmd = [
        blender_exe.as_posix(),
        "--background",
        "--factory-startup",
        "--python",
        generator_filepath.as_posix(),
        "--",
        f"instance_id={instance_id}",
        f"config={config.serialize()}",
    ]

    # Launch Blender, merging stderr into stdout, text mode for easy printing
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Print each line as it arrives
    assert process.stdout is not None
    for line in process.stdout:
        if config.nocapture:
            print(decode_bpyprint(line), end="")
        else:
            if is_bpyprint(line):
                print(decode_bpyprint(line), end="")

    # Wait for Blender to exit, then return its code
    return process.wait()

def main() -> None:
    """Main function"""

    parser = argparse.ArgumentParser(description="Simple test runner")
    
    parser.add_argument(
        "-cf", "--config-file", action="store_true", help="Show help for the config file"
    )

    parser.add_argument(
        "-be", "--blender-exe", help="Path to the blender executable"
    )

    # parser.add_argument(
    #     "--show-config",
    #     action="store_true",
    #     help="Show the current configuration and exit",
    # )

    # Positional argument for the test file or directory
    parser.add_argument(
        "collector_string",
        nargs="?",
        default=".",
        help=SessionConfig.get_attr_help("collector_string"),
    )

    parser.add_argument(
        "-s",
        "--nocapture",
        action="store_true",
        help=SessionConfig.get_attr_help("nocapture"),
    )

    parser.add_argument(
        "-k",
        "--keyword",
        help=SessionConfig.get_attr_help("keyword"),
    )

    parser.add_argument(
        "-bel",
        "--blender-exe-id-list",
        help=ConfigFilePackageLevel.get_attr_help("blender_exe_id_list"),
    )

    parser.add_argument(
        "-e",
        "--envfile",
        help=ConfigFilePackageLevel.get_attr_help("envfile"),
    )

    parser.add_argument(
        "-nrd",
        "--norecursedirs",
        nargs="*",
        help=ConfigFileBlenderLevel.get_attr_help("norecursedirs"),
    )

    args = parser.parse_args()
    
    if args.config_file:
        _print_config_file_help()
        sys.exit(0)

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
    # if args.show_config:
    #     print("Current configuration:")
    #     pprint(bpytest_config.__dict__)
    #     sys.exit(0)

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

        # ===========================================================
        # Create isolated installation if needed
        # ===========================================================
        _installation_temp_dir: Path | None = None
        if pyproject_data.get("isolate_installation", False):
            _installation_temp_dir, blender_exe = (
                _isolate_blender_installation(blender_exe)
            )

        # ===========================================================
        # Install python dependencies if needed
        # ===========================================================
        python_dependencies = pyproject_data.get("python_dependencies", [])
        if python_dependencies:
            _install_python_dependencies(
                blender_exe=blender_exe,
                python_dependencies=python_dependencies,
            )

        # ===========================================================
        # Execute the test session
        # ===========================================================
        return_code = _call_subprocess(
            blender_exe, bpytest_config, instance_id
        )
        return_codes.append(return_code)

        # ===========================================================
        # Clean up isolated installation if needed
        # ===========================================================
        if _installation_temp_dir is not None:
            print(
                f"Cleaning up isolated installation at {_installation_temp_dir} "
                f"for blender executable {blender_exe}"
            )
            shutil.rmtree(_installation_temp_dir)

    if any(code != 0 for code in return_codes):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
