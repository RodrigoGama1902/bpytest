from .fixtures import FixtureRequest as FixtureRequest, fixture as fixture
from pathlib import Path

MAX_TEMP_FOLDERS: int

def tmp_path(request: FixtureRequest) -> Path: ...
