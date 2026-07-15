import sqlite3
import threading
from ledgerflow import config
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.db_path = config.DB_PATH
        self.schema_path = config.BASE_DIR / "database" / "schema.sql"
        self._initialize_db()
        self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection with foreign key constraints enabled and dictionary row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _initialize_db(self):
        """Initializes the database schema and seeds default categories if empty."""
        db_existed = self.db_path.exists()

        if not db_existed:
            logger.info(
                f"Database file not found. Creating new database at {self.db_path}"
            )

        conn = self.get_connection()
        try:
            # Check if schema.sql exists and apply it
            if self.schema_path.exists():
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
                logger.info("Database schema applied successfully.")
            else:
                logger.error(f"Schema file not found at {self.schema_path}!")

            # Seed default categories
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            if count == 0:
                logger.info("Seeding default categories...")
                for category in config.DEFAULT_CATEGORIES:
                    cursor.execute(
                        "INSERT INTO categories (name, icon, color) VALUES (?, ?, ?)",
                        (category["name"], category["icon"], category["color"]),
                    )
                conn.commit()
                logger.info("Default categories seeded successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise e
        finally:
            conn.close()
