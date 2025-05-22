import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def get_bpyconfig_attr_help(attr: str) -> str:
    """Get the help string for a given attribute in BpyTestConfig"""

    # Get the field object for the specified attribute
    field_obj = BpyTestConfig.__dataclass_fields__.get(attr)
    if field_obj is None:
        return f"No help available for {attr}"

    # Get the help string from the field's metadata
    help_str = field_obj.metadata.get("help", "No help available")
    return help_str


@dataclass
class BpyTestConfig:
    """Class that represents the configuration of the test session."""

    blender_exe: Path | None = field(
        default=None, metadata={"help": "Path to blender executable"}
    )
    pythonpath: Path = field(
        default=Path.cwd(), metadata={"help": "Path python cwd"}
    )
    nocapture: bool = field(
        default=False,
        metadata={
            "help": (
                "Disables output capture,"
                "if True, the test output will be displayed in the console."
            )
        },
    )
    module_list: str = field(
        default="",
        metadata={
            "help": (
                "List of modules to be loaded before running the tests, "
                "separated by commas."
            )
        },
    )
    blender_exe_id_list: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of blender executable ids to be used for the test session, "
                "each specified ID will be used to find the corresponding env variable with the path to the blender executable. "
                "e.g. 'blender_3_5' will look for the env variable 'BLENDER_3_5' and use its value as the path to the blender executable. "
                "This is useful for testing multiple versions of blender in the same test session."
            )
        },
    )
    norecursedirs: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of directories to be excluded from the test discovery, "
                "separated by commas. "
            )
        },
    )
    include: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of directories to be included in the test discovery, "
                "separated by commas. "
            )
        },
    )
    collector_string: str = field(
        default="", metadata={"help": "Test file or directory path"}
    )
    keyword: str = field(
        default="",
        metadata={
            "help": "Run only tests that match the given keyword expression"
        },
    )

    def load_from_dict(self, data: dict[str, Any]):
        """Loads the config from a dict"""
        for key, value in data.items():

            if key == "blender_exe":
                setattr(self, key, Path(value))
                continue
            if key == "blender_exe_id_list":
                # check if value is a list
                if isinstance(value, str):
                    value = value.split(",")
                for idx, i in enumerate(value):
                    value[idx] = i.replace("'", "").strip()
                setattr(self, key, value)
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
