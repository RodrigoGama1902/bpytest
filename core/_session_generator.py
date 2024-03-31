"""This module is the entry point for the session blender subprocess."""

import json
import sys
import traceback

import bpy

try:
    bpy.ops.preferences.addon_enable(module="bpytest")
    from bpytest.core.entity import BpyTestConfig
    from bpytest.core.session import wrap_session
except ModuleNotFoundError:
    print(
        "ModuleNotFoundError: Make sure bpytest is installed"
        f"in your blender environment. blender_exe: {bpy.app.binary_path}",
    )
    sys.exit(1)


def main(config: BpyTestConfig):
    """Main function"""

    wrap_session(config)


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
