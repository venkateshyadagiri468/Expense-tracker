from ledgerflow.database.database import DatabaseManager
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


def run_migrations():
    """Runs outstanding database migrations. Currently verifies schema init."""
    logger.info("Running database migrations check...")
    try:
        # Singleton instantiation automatically initializes schema and seeds categories
        db_mgr = DatabaseManager()
        # Verify schema table presence
        conn = db_mgr.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        logger.info(f"Database migrations check completed. Existing tables: {tables}")
        return True
    except Exception as e:
        logger.error(f"Migration check failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    run_migrations()
