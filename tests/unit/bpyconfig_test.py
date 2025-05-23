import json
from pathlib import Path

from bpytest_config import BpyTestConfig


def test_serialize():
    """Test converting configuration to a dictionary."""

    config = BpyTestConfig()    
    config.pythonpath = Path("/path/to/python")
    config.link_addons = ["test_module"]
    config.enable_addons = ["test_module"]
    config.norecursedirs = ["dir1", "dir2"]
    config.include = ["test1", "test2"]
    config.collector_string = "test_file_or_directory"
    config.keyword = "test_keyword"
    config.nocapture = True

    json_string = config.serialize()
    assert json.loads(json_string) == {
        "pythonpath": "/path/to/python",
        "link_addons": ["test_module"],
        "enable_addons": ["test_module"],
        "norecursedirs": ["dir1", "dir2"],
        "include": ["test1", "test2"],
        "collector_string": "test_file_or_directory",
        "keyword": "test_keyword",
        "nocapture": True,
    }, "JSON string does not match expected dictionary"
    assert json_string == (
        '{"pythonpath": "/path/to/python",'
        ' "link_addons": ["test_module"],'
        ' "enable_addons": ["test_module"],'
        ' "norecursedirs": ["dir1", "dir2"],'
        ' "include": ["test1", "test2"],'
        ' "collector_string": "test_file_or_directory",'
        ' "keyword": "test_keyword",'
        ' "nocapture": true}'
    ), "JSON string does not match expected string"


def test_deserialize():
    """Test loading configuration from a dictionary."""

    config = BpyTestConfig()
    config.deserialize(
        (
            '{"pythonpath": "/path/to/python",'
            ' "nocapture": true,'
            ' "enable_addons": ["test_module"],'
            ' "norecursedirs": ["dir1", "dir2"],'
            ' "include": ["test1", "test2"],'
            ' "collector_string": "test_file_or_directory",'
            ' "keyword": "test_keyword"}'
        )
    )
    assert config.pythonpath == Path("/path/to/python")
    assert config.nocapture is True
    assert config.enable_addons == ["test_module"]
    assert config.norecursedirs == ["dir1", "dir2"]
    assert config.include == ["test1", "test2"]


def test_serialization_and_deserialization():
    """Test serialization and loading of configuration."""

    config = BpyTestConfig()
    config.pythonpath = Path("/path/to/python")
    config.nocapture = True
    config.enable_addons = ["test_module"]
    config.norecursedirs = ["dir1", "dir2"]
    config.include = ["test1", "test2"]
    config.collector_string = "test_file_or_directory"
    config.keyword = "test_keyword"

    json_string = config.serialize() # Serialize to JSON

    new_config = BpyTestConfig()
    new_config.deserialize(json_string)

    assert new_config.pythonpath == config.pythonpath
    assert new_config.nocapture == config.nocapture
    assert new_config.enable_addons == config.enable_addons
    assert new_config.norecursedirs == config.norecursedirs
    assert new_config.include == config.include
    assert new_config.collector_string == config.collector_string
    assert new_config.keyword == config.keyword
    
