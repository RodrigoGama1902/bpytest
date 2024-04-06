import tempfile
from pathlib import Path

from .fixtures import FixtureRequest, fixture

MAX_TEMP_FOLDERS = 3


def _get_default_bpytest_temp_dir() -> Path:
    """Get the default pytest temporary directory."""

    path = Path(tempfile.gettempdir()) / "bpytest"
    if not path.exists():
        path.mkdir()

    return path


def _recursive_remove(path: Path):
    """Recursively remove a directory."""
    for child in path.iterdir():
        if child.is_dir():
            _recursive_remove(child)
        else:
            child.unlink()
    path.rmdir()


def _get_test_temp_directory(test_name: str, session_id: int) -> Path:
    """Get the temporary directory for the tests."""
    temp_directory = (
        _get_default_bpytest_temp_dir() / str(session_id) / test_name
    )
    temp_directory.mkdir(exist_ok=True, parents=True)
    return temp_directory


def _delete_old_temp_folders():
    """Delete old temporary folders."""
    temp_directory = _get_default_bpytest_temp_dir()
    temp_folders = sorted(
        temp_directory.iterdir(), key=lambda x: x.stat().st_ctime
    )
    for folder in temp_folders[:-MAX_TEMP_FOLDERS]:
        _recursive_remove(folder)


@fixture
def tmp_path(request: FixtureRequest) -> Path:
    """Fixture to create a temporary path."""

    _delete_old_temp_folders()
    return _get_test_temp_directory(
        test_name=request.name, session_id=request.session_info.id
    )
