class InvalidFixtureName(Exception):
    """Exception raised when an invalid fixture name is provided"""

    def __init__(self, fixture_name: str):
        self.fixture_name = fixture_name

    def __str__(self):
        return f"Invalid fixture name for test: {self.fixture_name}"
