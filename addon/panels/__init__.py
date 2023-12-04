from .main_panel import BPYTEST_PT_MainPanel

classes = (
    BPYTEST_PT_MainPanel,
)


def register_panels():
    from bpy.utils import register_class  #type:ignore
    for cls in classes:
        register_class(cls)
    
def unregister_panels():
    from bpy.utils import unregister_class  #type:ignore
    for cls in reversed(classes):
        unregister_class(cls)