import bpy # type:ignore

def test_simple_print():
    print("Test should pass")

def test_failed():
    print("Test Should fail")
    assert False

def test_failed_with_false():
    print("Test Should fail")
    return False

def test_cube_creation():
    print("Test should pass")

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.object
    assert cube

    