# =============================================================================
# This is just a script that will be executed in a subprocess inside Blender.exe
# =============================================================================

import sys
import bpy #type:ignore
import traceback

from pathlib import Path

from bpytest.bpytest.test_manager.process import execute

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
    
    enable_module_list(module_list)
    execution_result = execute(pythonpath, filepath, function_name)
    
    if not execution_result.success:
        print("\n".join(execution_result.result_lines))
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
