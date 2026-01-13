import os
from pathlib import Path
from typing import Any

import yaml
from configlite.config import BaseConfig


class ConfigTest(BaseConfig):
    foo: str = "foo"
    val: int = 10


def verify_variable(file: Path, name: str, value: Any) -> bool:
    """Verify that a variable in the config file has the expected value.

    Args:
        file:
            The path to the config file.
        name:
            The name of the variable to check.
        value:
            The expected value of the variable.

    Returns:
        True if the variable has the expected value, False otherwise.

    """
    with file.open() as o:
        data = yaml.safe_load(o)

    return data.get(name, None) == value


def test_restore_file(capsys):
    file = Path("test.yaml")

    config = ConfigTest(file)

    with file.open("w+") as o:
        o.write("")  # create an empty file

    assert config.foo == "foo"
    assert config.val == 10

    assert os.path.exists(f"{file}.bk")
    assert "WARNING" in capsys.readouterr().out

    assert verify_variable(file, "foo", "foo")


def test_restore_file_priority(capsys):
    file_a = Path("test_a.yaml")
    file_b = Path("test_b.yaml")

    config = ConfigTest(paths=[file_a, file_b])

    with file_a.open("w+") as o:
        o.write("")  # create an empty file

    assert config.foo == "foo"
    assert config.val == 10

    assert os.path.exists(f"{file_a}.bk")
    assert "WARNING" in capsys.readouterr().out

    assert verify_variable(file_a, "foo", "foo")

def test_mangled_file(capsys):
    file = Path("test.yaml")

    config = ConfigTest(file)

    with file.open("w+") as o:
        o.write("foo")  # create a broken file

    assert config.foo == "foo"
    assert config.val == 10

    assert os.path.exists(f"{file}.bk")
    assert "WARNING" in capsys.readouterr().out


def test_delete_variable():
    file = Path("test.yaml")

    config = ConfigTest(file)

    assert config.foo == "foo"
    assert config.val == 10

    # get the file content for modification
    with file.open() as o:
        data = yaml.safe_load(o)
        assert data["foo"] == "foo"
    # delete foo and write the changes
    del data["foo"]
    with file.open("w+") as o:
        yaml.dump(data, o)
    # make sure it's gone
    assert not verify_variable(file, "foo", "foo")
    # we should still have the default value
    assert config.foo == "foo"
    # check that it's been added back to the config
    assert verify_variable(file, "foo", "foo")


def test_modify_variable():
    """Test that modifying the config updates the file correctly."""
    class ConfigTest_1(BaseConfig):
        foo: str = "foo"

    class ConfigTest_2(BaseConfig):
        foo: str = "foo"
        new: str = "new_value"

    cfg = ConfigTest_1("test.yaml")
    assert cfg.foo == "foo"
    assert verify_variable(cfg.path, "foo", "foo")

    cfg = ConfigTest_2("test.yaml")
    assert verify_variable(cfg.path, "foo", "foo")
    assert verify_variable(cfg.path, "new", "new_value")
