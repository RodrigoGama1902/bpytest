import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BLENDER_MODULE_PATH = Path(__file__).parent / "blender_module"

@dataclass
class BpyTestConfig:
    """Class that represents the configuration of the test session.

    :param pythonpath: Path python cwd
    :param nocapture: Show test log
    :param module_list: List of modules to be loaded before running the tests
    :param blender_exe: Path to blender executable

    """

    pythonpath: Path = field(default=Path.cwd())
    nocapture: bool = field(default=False)
    module_list: str = field(default="")
    blender_exe: Path | None = field(default=None)
    norecursedirs: list[str] = field(default_factory=list)
    include : list[str] = field(default_factory=list)

    collector_string: str = field(default="")
    keyword: str = field(default="")

    def load_from_dict(self, data: dict[str, Any]):
        """Loads the config from a dict"""
        for key, value in data.items():

            if key == "blender_exe":
                setattr(self, key, Path(value))
                continue

            if value == "True":
                setattr(self, key, True)
            elif value == "False":
                setattr(self, key, False)
            elif value == "None":
                setattr(self, key, None)
            elif value.startswith("[") and value.endswith("]"):
                value = value[1:-1].split(",")
                for idx, i in enumerate(value):
                    value[idx] = i.replace("'", "").strip()
                setattr(self, key, value)
            elif hasattr(self, key):
                field_type = getattr(
                    self.__dataclass_fields__[key], "type", None
                )
                if field_type is not None:
                    # Handle special cases, such as Path
                    if field_type == Path:
                        setattr(self, key, Path(value))
                    else:
                        setattr(self, key, field_type(value))
                else:
                    setattr(self, key, value)

    def load_from_pyproject_toml(self, pyproject_toml_path: Path):
        """Loads the config file from pyproject.toml"""

        import toml  # type: ignore

        try:
            if not pyproject_toml_path.exists():
                raise Exception("pyproject.toml not found")

            pyproject_toml = toml.load(pyproject_toml_path)["tool"]["bpytest"]
        except KeyError:
            print("tool.bpytest not found")
            return

        self.pythonpath = Path(pyproject_toml.get("pythonpath", "")).absolute()
        self.nocapture = pyproject_toml.get("nocapture", False)
        self.module_list = pyproject_toml.get("module_list", "")
        self.norecursedirs = pyproject_toml.get("norecursedirs", [])
        self.blender_exe = Path(pyproject_toml.get("blender_exe", Path.cwd()))
        self.include = pyproject_toml.get("include", [])

    def as_dict(self) -> dict[str, Any]:
        """Returns the config as a json"""

        json_data: dict[str, Any] = {}

        for key, value in self.__dict__.items():
            # check if is enum
            if hasattr(value, "value"):
                json_data[key] = value.value
            else:
                json_data[key] = str(value)

        return json_data

    def as_json(self) -> str:
        """Returns the config as a json"""

        return json.dumps(self.as_dict())

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

    args = parser.parse_args()

    bpytest_config: BpyTestConfig = BpyTestConfig()

    pyproject_path = Path.cwd() / "pyproject.toml"
    if pyproject_path.exists():
        bpytest_config.load_from_pyproject_toml(pyproject_path)

    bpytest_config.nocapture = args.nocapture

    if args.keyword is not None:
        bpytest_config.keyword = args.keyword
    if args.collector_string is not None:
        bpytest_config.collector_string = args.collector_string
    if args.norecursedirs is not None:
        bpytest_config.norecursedirs = args.norecursedirs

    if bpytest_config.blender_exe is None:
        print("Blender executable not specified")
        sys.exit(1)
    if not bpytest_config.blender_exe.exists():
        print("Path to blender executable does not exist")
        sys.exit(1)

    sys.exit(_call_subprocess(bpytest_config))


if __name__ == "__main__":
    main()
