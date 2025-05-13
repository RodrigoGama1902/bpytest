"""This module is the entry point for the session blender subprocess."""

import json
import sys
import traceback
from pathlib import Path

# Append current work directory to sys.path so bpytest is accessible 
# inside the blender subprocess
sys.path.append(Path(__file__).parent.as_posix())
from bpytest import BpyTestConfig, wrap_session  # pylint: disable=wrong-import-position


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
