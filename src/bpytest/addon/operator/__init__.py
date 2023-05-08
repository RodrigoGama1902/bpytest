

from .run_tests import BPYTEST_OT_Tests


classes = (
    BPYTEST_OT_Tests,
)


def register_operators():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister_operators():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)