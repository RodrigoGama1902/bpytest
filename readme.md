# bpytest

bpytest is a unit testing framework inspired by pytest that seamlessly integrates with Blender. It allows developers to create unit tests for add-ons within the Blender environment. The aim is to provide a familiar testing framework for Blender users based on a well-established test framework. Additionally, bpytest is designed to be simple to install and start using, ensuring that developers can quickly incorporate testing into their Blender add-on development workflow.

Key Features:

- Stand-alone Testing: Execute tests independently of Blender directly from any terminal environment.
- In-Blender Testing: Run tests within Blender, enabling developers to observe real-time test results during runtime.
- Simplified Assertions: Write cleaner and more readable assertions with Pytest-like assertion syntax.
- CLI Interface: CLI based on pytest for convenient test management.
- Fixtures: System inspired by Pytest for easy setup and teardown of test environments with scope support.

## CLI usage example

```bash
bpytest tests/unit/test_file.py::test_function
```
```bash
bpytest -s -k "test_function" 
```

## Test File Example

```python
import bpytest
import bpy

@bpytest.fixture(scope="session")
def session():
    """Create a session for some random rest API"""	
    session = Session()
    yield session
    session.close()

@bpytest.fixture
def blender_object():
    """Create a blender object"""
    bpy.ops.mesh.primitive_cube_add()
    return bpy.context.object

def test_session_upload(session_fixture, blender_object):
    """Test session.say_hello() method."""	
    assert session_fixture.upload_object_name(blender_object.name)
```

## Documentation
For detailed usage instructions and examples, please refer to the documentation [Work in progress].

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests on this repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.