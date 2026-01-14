import pytest
from MineDB.basicCommands import BasicCommands


class DummyDB(BasicCommands):
    def __init__(self):
        self.existing_db = {}


@pytest.fixture
def db():
    return DummyDB()


def test_create_database(db):
    db.createDB("testdb")
    assert "testdb" in db.existing_db


def test_create_collection(db):
    db.createDB("testdb")
    db.createCollection(
        "testdb",
        "users",
        id="int",
        active="bool"
    )
    assert "users" in db.existing_db["testdb"]


def test_duplicate_database_raises(db):
    db.createDB("testdb")
    with pytest.raises(ValueError):
        db.createDB("testdb")


def test_duplicate_collection_raises(db):
    db.createDB("testdb")
    db.createCollection("testdb", "users", id="int")
    with pytest.raises(ValueError):
        db.createCollection("testdb", "users", id="int")


def test_alter_add_field(db):
    db.createDB("testdb")
    db.createCollection("testdb", "users", id="int")

    db.alterAddField("testdb", "users", "active", "bool")
    assert "active" in db.existing_db["testdb"]["users"]


def test_alter_drop_field(db):
    db.createDB("testdb")
    db.createCollection("testdb", "users", id="int", active="bool")

    db.alterDropField("testdb", "users", "active")
    assert "active" not in db.existing_db["testdb"]["users"]


def test_alter_field_type_conversion(db):
    db.createDB("testdb")
    db.createCollection("testdb", "users", age="int")

    db.existing_db["testdb"]["users"]["age"]["items"] = [1, 2, 3]

    db.alterFieldType("testdb", "users", "age", "float")

    assert db.existing_db["testdb"]["users"]["age"]["items"] == [1.0, 2.0, 3.0]


def test_rename_database(db):
    db.createDB("old")
    db.renameDB("old", "new")

    assert "new" in db.existing_db
    assert "old" not in db.existing_db


def test_rename_collection(db):
    db.createDB("testdb")
    db.createCollection("testdb", "users", id="int")

    db.renameCollection("testdb", "users", "accounts")
    assert "accounts" in db.existing_db["testdb"]
