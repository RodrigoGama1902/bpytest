import bpy  #type:ignore

from .addon_props import BPYTEST_AddonMainProps

classes = (
    BPYTEST_AddonMainProps,
)

def register_properties():
    from bpy.utils import register_class  #type:ignore
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.bpy_test = bpy.props.PointerProperty(type= BPYTEST_AddonMainProps)

def unregister_properties():
    from bpy.utils import unregister_class  #type:ignore
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.bpy_test