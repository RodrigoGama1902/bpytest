"""This module is the entry point for the session blender subprocess."""

import json
import shutil
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

import bpy


def _copy_files_recursive(src: Path, dst: Path, ignore_dirs: list[str]):
    """Copy files recursively from src to dst"""

    for item in src.iterdir():
        if item.is_dir():
            if item.name in ignore_dirs:
                continue
            shutil.copytree(item, dst / item.name)
        else:
            shutil.copy2(item, dst / item.name)


def _create_temp_addon_zip(addon_dir: Path) -> Path:
    """Create a temporary zip file with the addon contents"""

    temp_dir = Path(tempfile.mkdtemp(prefix="bpytest_addon_"))
    module_dir = temp_dir / "bpytest" / "bpytest"
    module_dir.mkdir(parents=True)

    _copy_files_recursive(
        addon_dir,
        module_dir,
        ignore_dirs=["__pycache__", ".git", ".venv", ".pytest_cache"],
    )

    temp_zip = module_dir.parent.parent / "bpytest.zip"
    with zipfile.ZipFile(temp_zip, "w") as zipf:
        for file in module_dir.parent.rglob("*"):
            zipf.write(file, file.relative_to(module_dir.parent))

    return temp_zip


try:
    bpy.ops.preferences.addon_enable(module="bpytest")
except:  # pylint: disable=bare-except
    addon_zip = _create_temp_addon_zip(Path(__file__).parent.parent)
    bpy.ops.preferences.addon_install(
        filepath=addon_zip.as_posix(), overwrite=True
    )
    bpy.ops.preferences.addon_enable(module="bpytest")

try:
    from bpytest.bpytest.entity import BpyTestConfig
    from bpytest.bpytest.session import wrap_session
except ModuleNotFoundError:
    print(
        "ModuleNotFoundError: Make sure bpytest is installed"
        f"in your blender environment. blender_exe: {bpy.app.binary_path}",
    )
    sys.exit(1)


def main(config: BpyTestConfig):
    """Main function"""

    for path in config.include:
        sys.path.append(path)
    
    sys.exit(wrap_session(config))


try:
    # Get the JSON string from command-line arguments
    data_json: str = ""
    for arg in sys.argv:
        if arg.startswith("config="):
            data_json = arg[7:]
            break
    if not data_json:
        raise ValueError("No config argument found")

    # Deserialize the JSON string back to a Python object
    data = json.loads(data_json)

    config = BpyTestConfig()
    config.load_from_dict(data)

    main(config)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    raise e
