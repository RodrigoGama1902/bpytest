import bpy


class BPYTEST_PT_MainPanel(bpy.types.Panel):
    bl_label = "Main Panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BPYTest'

    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True

        props = context.scene.bpy_test

        box = layout.box()
        box.prop(props, "source_directory")

        row = box.row()
        row.scale_y = 1.3
        row.operator("bpytest.run_tests", text = "Run Tests").source_directory = props.source_directory

