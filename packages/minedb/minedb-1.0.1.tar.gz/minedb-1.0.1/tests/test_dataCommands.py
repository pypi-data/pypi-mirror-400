import pytest
from MineDB.dataCommands import DataCommands
from MineDB.basicCommands import BasicCommands


class DummyDB(BasicCommands, DataCommands):
    def __init__(self):
        self.existing_db = {
            "app": {
                "settings": {
                    "theme": {"dataType": "text", "items": []},
                    "notifications": {"dataType": "bool", "items": []},
                }
            }
        }
        self.currDB = "app"
        self.currColl = "settings"


@pytest.fixture
def db():
    return DummyDB()


def test_load_valid_data(db):
    db.load(theme="dark", notifications=True)

    assert db.existing_db["app"]["settings"]["theme"]["items"] == ["dark"]
    assert db.existing_db["app"]["settings"]["notifications"]["items"] == [True]


def test_load_incomplete_data_raises(db):
    with pytest.raises(ValueError):
        db.load(theme="dark")


def test_load_invalid_type_raises(db):
    with pytest.raises(ValueError):
        db.load(theme=123, notifications=True)


def test_modify_data(db):
    db.load(theme="dark", notifications=True)
    db.modify("theme", "dark", "notifications", False)

    assert db.existing_db["app"]["settings"]["notifications"]["items"] == [False]


def test_modify_missing_value_raises(db):
    db.load(theme="dark", notifications=True)
    with pytest.raises(ValueError):
        db.modify("theme", "light", "notifications", False)


def test_remove_data(db):
    db.load(theme="dark", notifications=True)
    db.remove("theme", "dark")

    assert db.existing_db["app"]["settings"]["theme"]["items"] == []
    assert db.existing_db["app"]["settings"]["notifications"]["items"] == []


def test_remove_missing_value_raises(db):
    db.load(theme="dark", notifications=True)
    with pytest.raises(ValueError):
        db.remove("theme", "light")


def test_no_index_drift(db):
    db.load(theme="dark", notifications=True)
    db.load(theme="light", notifications=False)
    db.remove("theme", "dark")

    assert db.existing_db["app"]["settings"]["theme"]["items"] == ["light"]
    assert db.existing_db["app"]["settings"]["notifications"]["items"] == [False]
