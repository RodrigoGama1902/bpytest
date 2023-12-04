import bpy #type:ignore

from bpytest.bpytest.manager import TestManager
from bpytest.bpytest.entity import BpyTestConfig, CollectorString
from bpytest.bpytest.collector import Collector

from pathlib import Path

class BPYTEST_OT_Tests(bpy.types.Operator):
    """Run Tests"""

    bl_idname = "bpytest.run_tests"
    bl_label = "Run detected unit tests"
    bl_options = {'REGISTER', 'UNDO'}
    
    collector_string : bpy.props.StringProperty(name = 'Addon Source Directory', 
                                                description = "Addon Source Directory",
                                                ) # type:ignore
    
    def execute(self, context):
        
        collector = Collector(
            collector_string=CollectorString(self.collector_string),
            keyword=""
        )
        
        bpytest_config = BpyTestConfig()
        bpytest_config.load_from_pyproject_toml(Path(self.collector_string, 'pyproject.toml'))
        bpytest_config.blender_exe = Path(bpy.app.binary_path)
        
        test_manager = TestManager(
            bpytest_config = bpytest_config, 
            collector = collector
        )
        
        if test_manager.bpytest_config.toggle_console:
            bpy.ops.wm.console_toggle()

        test_manager.execute()

        if test_manager.bpytest_config.toggle_console:
            bpy.ops.wm.console_toggle()

        self.report({'INFO'}, f"Failed: {test_manager.failed} Success: {test_manager.success} Total Time: {test_manager.total_time:.2f}")
        return {'FINISHED'}

