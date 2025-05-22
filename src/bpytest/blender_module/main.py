"""This module is the entry point for the session blender subprocess."""
import sys
import traceback
from pathlib import Path

# ===================================================================================
# Check to make sure that bpytest and bpytest_config modules are not already imported
# ===================================================================================
try:
    import bpytest  # pylint: disable=unused-import
    raise RuntimeError(
        "bpytest module already exists in the sys.modules blender python environment"
        " and this is not allowed. Make sure that there is no 'bpytest' "
        "installed directly in the blender python environment or as an addon."
    )
except ImportError:
    pass

try:
    import bpytest_config  # pylint: disable=unused-import
    raise RuntimeError(
        "bpytest_config module already exists in the sys.modules blender python environment"
        " and this is not allowed. Make sure that there is no 'bpytest_config' "
        "installed directly in the blender python environment or as an addon."
    )
except ImportError:
    pass

# ===================================================================================
# Add the bpytest and bpytest_config modules to the sys.path
# ===================================================================================
# Append src/bpytest/common so any common module that is accessible
# to the main entry point is also accessible inside the blender subprocess
sys.path.append(Path(Path(__file__).parent.parent / "common").as_posix())
from bpytest_config import BpyTestConfig  # pylint: disable=wrong-import-position

# Append current work directory to sys.path so bpytest is accessible
# inside the blender subprocess
sys.path.append(Path(__file__).parent.as_posix())
from bpytest import wrap_session  # pylint: disable=wrong-import-position


# ===================================================================================
# End of imports and sys.path modifications
# ===================================================================================
def main(config: BpyTestConfig, instance_id: str) -> int:
    """Main function"""

    for path in config.include:
        sys.path.append(path)
    
    sys.exit(wrap_session(config, instance_id))


try:
    # Get the JSON string from command-line arguments
    instance_id = ""
    data_json: str = ""
    for arg in sys.argv:
        if arg.startswith("config="):
            data_json = arg[7:]
        if arg.startswith("instance_id"):
            instance_id = arg.split("=")[1]

    if not data_json:
        raise ValueError("No config argument found")
    if not instance_id:
        raise ValueError("No instance_id argument found")

    config = BpyTestConfig()
    config.load_from_json(data_json)

    main(config, instance_id)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    raise e
