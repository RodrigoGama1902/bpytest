"""This module is the entry point for the session blender subprocess."""

import json
import sys
import traceback
from pathlib import Path

# Append src/bpytest/common so any common module that is accessible
# to the main entry point is also accessible inside the blender subprocess
sys.path.append(Path(Path(__file__).parent.parent / "common").as_posix())
from bpytest_config import BpyTestConfig  # pylint: disable=wrong-import-position

# Append current work directory to sys.path so bpytest is accessible
# inside the blender subprocess
sys.path.append(Path(__file__).parent.as_posix())
from bpytest import wrap_session  # pylint: disable=wrong-import-position


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
    
    config = BpyTestConfig()
    config.load_from_json(data_json)

    main(config)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    raise e
