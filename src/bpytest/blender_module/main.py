"""This module is the entry point for the session blender subprocess."""
import os
import sys
import traceback
from pathlib import Path

import bpy

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
    
def _link_addons(link_addons: list[str]) -> list[str]:
    """Link the specified addons to the user addons directory
    
    Returns:
        list[str]: List of addons to be enabled
    """
    blender_data = Path(bpy.utils.resource_path("USER"))
    addons_path = blender_data / "scripts" / "addons"
    if not addons_path.exists():
        addons_path.mkdir(parents=True, exist_ok=True)

    # link directories to here
    addons_to_enable = []
    for addon in link_addons:
        addon_path = Path(addon).absolute().resolve()
        if not addon_path.exists():
            print(f"Failed to link addon {addon_path}, it does not exist")
            continue

        addon_link = addons_path / addon_path.name
        if not addon_link.exists():
            os.symlink(addon_path, addon_link, target_is_directory=True)        
        addons_to_enable.append(addon_path.name)
        
    return addons_to_enable
try:
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
    
    if config.link_addons:
        new_addons_to_enable = _link_addons(config.link_addons)
        # Add the linked addons to the enable_addons list
        config.enable_addons = config.enable_addons + new_addons_to_enable
        print(f"Linked addons added to enable list: {new_addons_to_enable}")

    main(config, instance_id)
except Exception as e:
    print(e)
    print(traceback.format_exc())
    raise e
