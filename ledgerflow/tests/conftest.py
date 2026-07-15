import pytest
from ledgerflow import config
from ledgerflow.database.database import DatabaseManager


@pytest.fixture(autouse=True)
def use_test_db(tmp_path):
    """Sets a temporary database for the duration of the test run."""
    # Redirect DB path to a temporary test database file
    test_db = tmp_path / "test_ledger.db"
    config.DB_PATH = test_db

    # Reset Singleton initialization state to force re-init
    DatabaseManager._instance = None
    db_mgr = DatabaseManager()

    yield db_mgr

    # Close any open handlers/state if needed
    DatabaseManager._instance = None
