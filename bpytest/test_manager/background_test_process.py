# =============================================================================
# This is just a script that will be executed in a subprocess inside Blender.exe
# =============================================================================

import sys
import bpy #type:ignore
import importlib.util
import traceback

from pathlib import Path

for arg in sys.argv:
    if arg.startswith("filepath:"):
        filepath : Path = Path(arg[9:])
    if arg.startswith("pythonpath:"):
        pythonpath : Path = Path(arg[11:])
    if arg.startswith("function_name:"):
        function_name : str = arg[14:]
    if arg.startswith("module_list:"):
        module_list : list = arg[12:].split(",")

def enable_module_list(module_list : list): 

    for module in module_list:
        if module.strip() != "":
            bpy.ops.preferences.addon_enable(module=module.strip())

def main():

    sys.path.append(pythonpath.__str__())

    spec = importlib.util.spec_from_file_location(filepath.stem,filepath)  
    test_file = importlib.util.module_from_spec(spec) # type:ignore
    spec.loader.exec_module(test_file) # type:ignore
        
    obj = getattr(test_file, function_name)

    enable_module_list(module_list)

    if hasattr(obj, "__call__"): 
        result = obj()

    if result == False:
        return False

    return True

try:
    result = main()
    if not result:
        raise Exception("Test failed, returned False")
except:
    print(traceback.print_exc())
    sys.exit(1)

sys.exit(0)
