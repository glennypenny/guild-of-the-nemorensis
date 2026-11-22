import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from build_db import build  # noqa: E402


@pytest.fixture(scope="session")
def built_db(tmp_path_factory):
    """Build one real database for the whole test session."""
    db_path = tmp_path_factory.mktemp("database") / "guild.db"
    build(db_path)
    return db_path


@pytest.fixture
def conn(built_db):
    """Open a connection and roll back anything a test changes."""
    connection = sqlite3.connect(built_db)
    connection.execute("PRAGMA foreign_keys = ON")
    yield connection
    connection.rollback()
    connection.close()
