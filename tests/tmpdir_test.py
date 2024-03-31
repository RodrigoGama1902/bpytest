from pathlib import Path


def test_tmp_path(tmp_path: Path):
    """Test the built-in fixture"""

    print("Test should pass")
    print(tmp_path)
    assert tmp_path


def test_tmp_path_2(tmp_path: Path):
    """Test the built-in fixture"""

    print("Test should pass")
    print(tmp_path)
    assert tmp_path
