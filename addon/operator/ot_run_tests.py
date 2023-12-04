import bpy #type:ignore

from bpytest.bpytest.test_manager import TestManager, ConfigFile

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
        
        config_file = ConfigFile()
        config_file.load_from_pyproject_toml(Path(self.source_directory, 'pyproject.toml'))
        config_file.blender_exe = Path(bpy.app.binary_path)
        
        test_manager = TestManager(
            config_file = config_file, 
            source_directory = Path(self.source_directory))
        
        if test_manager.config_file.toggle_console:
            bpy.ops.wm.console_toggle()

        test_manager.execute()

        if test_manager.config_file.toggle_console:
            bpy.ops.wm.console_toggle()

        self.report({'INFO'}, f"Failed: {test_manager.failed} Success: {test_manager.success} Total Time: {test_manager.total_time:.2f}")
        return {'FINISHED'}

