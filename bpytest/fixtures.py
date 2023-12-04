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
