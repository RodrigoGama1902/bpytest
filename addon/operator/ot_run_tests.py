import bpy #type:ignore

from ..test_manager import TestManager
from pathlib import Path


class BPYTEST_OT_Tests(bpy.types.Operator):
    """Run Tests"""

    bl_idname = "bpytest.run_tests"
    bl_label = "Run detected unit tests"
    bl_options = {'REGISTER', 'UNDO'}
    
    source_directory : bpy.props.StringProperty(name = 'Addon Source Directory', 
                                                description = "Addon Source Directory",
                                                ) # type:ignore
    
    def execute(self, context):

        test_manager = TestManager(Path(self.source_directory))
        
        if test_manager.config_file.toggle_console:
            bpy.ops.wm.console_toggle()

        test_manager.execute()

        if test_manager.config_file.toggle_console:
            bpy.ops.wm.console_toggle()

        self.report({'INFO'}, f"Failed: {test_manager.failed} Success: {test_manager.success} Total Time: {test_manager.total_time:.2f}")
        return {'FINISHED'}

