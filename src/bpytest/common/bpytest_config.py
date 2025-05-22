import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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