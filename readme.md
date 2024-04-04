# bpytest

bpytest is a unit testing framework inspired by pytest that seamlessly integrates with Blender. It allows developers to create unit tests for add-ons within the Blender environment. The aim is to provide a familiar testing framework for Blender users based on a well-established tool.

Key Features:

- CLI Interface: CLI based on pytest for convenient test management.
- Stand-alone Testing: Execute tests independently of Blender directly from any terminal environment.
- In-Blender Testing: Run tests within Blender, enabling developers to observe real-time test results during runtime.
- Simplified Assertions: Write cleaner and more readable assertions with Pytest-like assertion syntax.
- Fixtures: Fixture system inspired by Pytest for easy setup and teardown of test environments with scope support.

## Command example

```bash
bpytest tests/unit/test_file.py::test_function
```
```bash
bpytest -s -k "test_function" 
```

## Test File Example

```python
import bpytest

@bpytest.fixture(scope="session")
def session():
    """Create a session."""	
    session = Session()
    yield session
    session.close()

@bpytest.fixture
def user_name():
    return "user_name"

def test_subtraction(session_fixture, user_name):
    """Test session.say_hello() method."""	
    assert session_fixture.say_hello(user_name)
```

## Compatibility
Compatible with Blender versions 3.5 and above.
Requires Python 3.11 or higher.

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests on this repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.