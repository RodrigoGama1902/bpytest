from _typeshed import Incomplete

class InvalidFixtureName(Exception):
    fixture_name: Incomplete
    def __init__(self, fixture_name: str) -> None: ...
