import sys
import importlib.util
import traceback

from pathlib import Path

for arg in sys.argv:
    if arg.startswith("filepath:"):
        filepath = Path(arg[9:])
    if arg.startswith("pythonpath:"):
        pythonpath = Path(arg[11:])
    if arg.startswith("function_name:"):
        function_name = arg[14:]

sys.path.append(pythonpath.__str__())

print("filepath: " + filepath.__str__())
print("pythonpath: " + pythonpath.__str__())
print("function_name: " + function_name)

spec = importlib.util.spec_from_file_location(filepath.stem,filepath)  
test_file = importlib.util.module_from_spec(spec) # type:ignore
spec.loader.exec_module(test_file) # type:ignore
    
obj = getattr(test_file, function_name)
failed = False

if hasattr(obj, "__call__"):
    
    try:
        obj()
    except Exception:
        failed = True
        traceback.print_exc()
        sys.exit(1)
