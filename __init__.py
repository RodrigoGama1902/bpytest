bl_info = {
    "name": "BPYtester",
    "description": "Unit Test for Blender Addons",
    "author": "Rodrigo Gama",
    "version": (0, 1, 0),
    "blender": (3, 5, 0),
    "location": "View3D",
    "category": "3D View"}


def register():
    from .addon.register import register_addon
    register_addon()


def unregister():
    from .addon.register import unregister_addon
    unregister_addon()

