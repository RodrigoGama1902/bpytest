"""
bpytest.common.bpytest_config
~~~~~~~~~~~~~~

Defines dataclasses to encapsulate configuration for running Blender-based bpytest sessions.

This class-inheritance structure aproache was chosen to allow for
a clear separation of concerns between package-level and Blender-session–specific settings.

Classes:
    _BaseConfig
        Shared logic for retrieving and formatting help text from dataclass metadata.
    _BaseConfigFile
        Base class for configuration dataclasses that are loaded from a file.
    ConfigFilePackageLevel
        Holds package-level settings (e.g., which Blender executables to use,
        environment file path, Python dependencies, installation isolation toggles).
    ConfigFileBlenderLevel
        Holds Blender-session–specific settings (e.g., pythonpath, addon links,
        discovery include/exclude patterns).
    SessionConfig
        Holds bpytest session flags (collector paths, keyword filters, capture
        behavior).
    BpyTestConfig
        Top-level composition of ConfigFileBlenderLevel and SessionConfig,
        responsible for serializing its state to JSON for passing as a single
        argument into the subprocessed Blender test runner, and deserializing
        inside Blender to configure discovery, addons, and test execution.
"""

import json
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class _BaseConfig:
    """Base class for configuration dataclasses."""

    @classmethod
    def get_attr_help(cls, attr: str) -> str:
        """Get the help string for a given attribute"""

        # Get the field object for the specified attribute
        field_obj = cls.__dataclass_fields__.get(attr)
        if field_obj is None:
            return f"No help available for {attr}"

        # Get the help string from the field's metadata
        help_str = field_obj.metadata.get("help", "No help available")
        return help_str
    
    @classmethod
    def help(cls, max_width: int = 110, field_width: int = 40) -> str:
        """
        Get the help string for all attributes, wrapped to `max_width` columns,
        with the field names left-aligned in a `field_width`-wide column.
        """
        lines: list[str] = []
        for attr, field_obj in cls.__dataclass_fields__.items():
            name = f"-> {attr}"
            # pad the name to exactly field_width characters
            prefix = name.ljust(field_width)
            # the raw help text
            desc = field_obj.metadata.get("help", "No help available")
            # wrap it, using prefix for the first line and indenting subsequent lines
            wrapped = textwrap.fill(
                desc,
                width=max_width,
                initial_indent=prefix,
                subsequent_indent=" " * field_width
            )
            wrapped += "\n"
            
            lines.append(wrapped)
        return "\n".join(lines)
    

@dataclass
class _BaseConfigFile(_BaseConfig):
    """Base class for configuration dataclasses that are loaded from a file."""

    def load_from_pyproject_data(self, pyproject_data: dict[str, Any]):
        """Populate attributes from pyproject.toml data"""
        for key, value in pyproject_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid attribute {key} for {self.__class__.__name__}")

@dataclass
class ConfigFilePackageLevel(_BaseConfigFile):
    """Attributes used on src/bpytest/main.py package level only"""

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

    envfile: str = field(
        default="",
        metadata={"help": "Path to the environment file"},
    )

    python_dependencies: list[str] = field(
        default_factory=list,
        metadata={
            "help": "List of python dependencies to be installed before running the tests, "
        },
    )

    isolate_installation: bool = field(
        default=False,
        metadata={
            "help": (
                "If set to True, the test session will run in an isolated Blender environment "
                "by duplicating the Blender installation folder and "
                "using that duplicate during testing. "
                "The duplicated folder will be removed after the test completes. "
                "For Blender versions 4.2 and newer, a 'portable' "
                "directory will be generated inside the installation path, "
                "ensuring Blender starts with a completely clean configuration."
            )
        },
    )
    
@dataclass
class ConfigFileBlenderLevel(_BaseConfigFile):
    """
    Attributes used inside the blender test session
    on src/bpytest/blender_module/main.py level
    """

    # TODO: pythonpath should receive a list of paths, not a single path
    # Confirm the behavior of the pythonpath in the test session
    pythonpath: Path = field(
        default=Path.cwd(), metadata={"help": "Path python cwd"}
    )

    link_addons: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of addon directories to be linked and enabled before running the tests. "
            )
        },
    )
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

    # TODO: Check if the include attr is not ambiguous with the pythonpath with
    # multiple paths
    include: list[str] = field(
        default_factory=list,
        metadata={
            "help": (
                "List of directories to be included in the test discovery, "
                "separated by commas. "
            )
        },
    )


@dataclass
class SessionConfig(_BaseConfig):
    """Class that represents the configuration of the test session."""

    collector_string: str = field(
        default="", metadata={"help": "Test file or directory path"}
    )
    keyword: str = field(
        default="",
        metadata={
            "help": "Run only tests that match the given keyword expression"
        },
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


# ====================================================================
# Main config class that will be used in the test session
# ====================================================================
@dataclass
class BpyTestConfig(SessionConfig,ConfigFileBlenderLevel,_BaseConfig):
    """This class encapsulates every setting needed to 
    run tests inside a Blender test session. 
    
    It bridges the “host” (package-level) environment and the Blender 
    subprocess by serializing its state to a JSON string, 
    which is then handed off as a single command-line argument. 
    
    When Blender spins up, it deserializes that JSON and applies 
    the configuration to orchestrate discovery, addon setup, 
    Python paths, and any other session options. 
    
    This serialization step is required because the Blender test 
    runner runs as a separate process that can only accept string arguments.
    """
    def load_from_pyproject_data(self, pyproject_data: dict[str, Any]):
        """Loads the config file from pyproject.toml"""        
        # Load based on SessionConfig and ConfigFileBlenderLevel attributes
        for field in SessionConfig.__dataclass_fields__.keys():
            if field in pyproject_data:
                setattr(self, field, pyproject_data[field])
        for field in ConfigFileBlenderLevel.__dataclass_fields__.keys():
            if field in pyproject_data:
                setattr(self, field, pyproject_data[field])

    def serialize(self) -> str:
        """Returns the config as a json"""

        json_data: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            # Handle Path objects, that is not supported by json
            if hasattr(value, "as_posix"):
                json_data[key] = value.as_posix()
                continue
            json_data[key] = value

        return json.dumps(json_data)
    
    def deserialize(self, json_string: str):
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
