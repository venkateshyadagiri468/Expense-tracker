from ledgerflow.database.database import DatabaseManager


class BaseRepository:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def get_connection(self):
        return self.db_manager.get_connection()
