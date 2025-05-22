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

    # ===========================================
    # Project Settings
    # ===========================================
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
    # install_addons: list[str] = field(
    #     default_factory=list,
    #     metadata={
    #         "help": (
    #             "List of addon zip files to be installed before running the tests, "
    #         )
    #     },
    # )
    
    link_addons: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of addon directories to be linked and enabled before running the tests. "
            )
        },
    )
    
    # disable_addons: list[str] = field(
    #     default_factory=list,
    #     metadata={
    #         "help": (
    #             "List of addon names to be disabled before running the tests, "
    #         )
    #     },
    # )
    
    
    enable_addons: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of already installed add-ons to be enabled before running the tests. "
                "If your add-on is already installed in the Blender installation that you will run the tests, "
                "use this option to enable it. "
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
    
    # ===========================================
    # Test Session Config
    # ===========================================
    collector_string: str = field(
        default="", metadata={"help": "Test file or directory path"}
    )
    keyword: str = field(
        default="",
        metadata={
            "help": "Run only tests that match the given keyword expression"
        },
    )

    def load_from_json(self, json_string: str):
        """Loads the config from a dict"""

        data: dict[str, Any] = json.loads(json_string)

        for key, value in data.items():
            try:
                field_type = getattr(
                    self.__dataclass_fields__[key], "type", None
                )
                if field_type is not None:
                    setattr(self, key, field_type(value))
                else:
                    setattr(self, key, value)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid value for {key}: {value} " f"({type(value)})"
                ) from exc

    def load_from_pyproject_data(self, pyproject_data : dict[str, Any]):
        """Loads the config file from pyproject.toml"""

        self.pythonpath = Path(pyproject_data.get("pythonpath", "")).absolute()
        self.nocapture = pyproject_data.get("nocapture", False)
        self.enable_addons = pyproject_data.get("enable_addons", [])
        self.norecursedirs = pyproject_data.get("norecursedirs", [])
        self.include = pyproject_data.get("include", [])
        self.link_addons = pyproject_data.get("link_addons", [])

    def as_json(self) -> str:
        """Returns the config as a json"""

        json_data: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            # Handle Path objects, that is not supported by json
            if hasattr(value, "as_posix"):
                json_data[key] = value.as_posix()
                continue
            json_data[key] = value

        return json.dumps(json_data)
