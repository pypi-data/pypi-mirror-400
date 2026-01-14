MineDB

MineDB is a lightweight, encrypted, dictionary-based local database written in Python.
It is designed to be simple, schema-safe, and usable directly after installation
without requiring any external database server.

PyPI: https://pypi.org/project/minedb/

MineDB is ideal for:
- Small to medium projects
- Local persistence
- Configuration storage
- Lightweight applications where SQLite or full databases are overkill


FEATURES
--------
- Encrypted local storage (Fernet encryption)
- Pure Python, pip-installable
- Schema-safe operations (no silent corruption)
- Dictionary-based column-oriented storage
- Safe schema evolution (add/drop/rename fields)
- Fully tested with pytest
- No external database required


INSTALLATION
------------
pip install minedb


QUICK START
-----------
from MineDB import MineDB

db = MineDB()

db.createDB("testdb")
db.createCollection(
    "testdb",
    "users",
    id="int",
    active="bool"
)

db.load(id=1, active=True)
db.load(id=2, active=False)

db.modify("id", 1, "active", False)
db.remove("id", 2)

db.save()


HOW MINEDB WORKS
----------------
- Data is stored as encrypted JSON on disk
- Each collection uses column-oriented storage
- All operations enforce schema consistency
- Partial writes and index drift are prevented by design

MineDB guarantees that all fields in a collection always remain aligned.


SCHEMA OPERATIONS
-----------------
Add field:
db.alterAddField("testdb", "users", "score", "float")

Drop field:
db.alterDropField("testdb", "users", "score")

Change field type (safe conversion):
db.alterFieldType("testdb", "users", "active", "int")


ENCRYPTION
----------
MineDB uses cryptography.Fernet for encryption.
- Data is always stored encrypted on disk
- Encryption key is generated on first run
- Key is reused safely across sessions

Note: MineDB encryption is intended for local protection,
not high-threat adversarial environments.


TESTING
-------
Run tests using:
pytest


REQUIREMENTS
------------
Python 3.9 or higher
cryptography


LICENSE
-------
MIT License (see LICENSE.txt)


AUTHOR
------
Harsh Singh Sikarwar


DISCLAIMER
----------
MineDB is intended for local and lightweight use cases.
It is not a replacement for full-scale database systems.
