import bpy # type:ignore

def test_simple_print():
    print("hi")

def test_failed():
    print("Should fail")
    assert False

def test_failed_with_false():
    return False

def test_cube_creation():

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    assert cube

    