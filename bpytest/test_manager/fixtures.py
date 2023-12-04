# fixtures.py

class FixtureManager:
    def __init__(self):
        self.fixtures = {}

    def register_fixture(self, name, fixture_func):
        self.fixtures[name] = fixture_func

    def get_fixture(self, name):
        if name not in self.fixtures:
            raise ValueError(f"Fixture '{name}' not registered.")
        return self.fixtures[name]

fixture_manager = FixtureManager()

def fixture(func):
    fixture_manager.register_fixture(func.__name__, func)
    return func

# Usage example in test file

from fixtures import fixture, fixture_manager

@fixture
def setup_teardown_example():
    print("\nSetting up...")

    # Any setup logic can go here

    yield  # This is where the test runs

    print("Tearing down...")

    # Any teardown logic can go here

def test_example(setup_teardown_example):
    print("Running test_example...")
    # Your test logic goes here

def test_another_example(setup_teardown_example):
    print("Running test_another_example...")
    # Your test logic goes here

if __name__ == "__main__":
    # Run tests
    for fixture_name in fixture_manager.fixtures:
        fixture_func = fixture_manager.get_fixture(fixture_name)
        if fixture_func.__name__.startswith("setup"):
            # Run setup fixtures before tests
            fixture_func()
    
    for test_name in dir():
        if test_name.startswith("test_"):
            # Run tests
            globals()[test_name]()
    
    for fixture_name in fixture_manager.fixtures:
        fixture_func = fixture_manager.get_fixture(fixture_name)
        if fixture_func.__name__.startswith("teardown"):
            # Run teardown fixtures after tests
            fixture_func()
