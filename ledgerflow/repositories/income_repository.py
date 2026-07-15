from typing import List, Optional
from datetime import date
from ledgerflow.repositories.base_repository import BaseRepository
from ledgerflow.models.income import Income
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class IncomeRepository(BaseRepository):
    def create(self, income: Income) -> Income:
        """Saves a new income entry to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO income (source, amount, received_date)
                VALUES (?, ?, ?)
                """,
                (
                    income.source,
                    income.amount,
                    income.received_date.strftime("%Y-%m-%d"),
                ),
            )
            conn.commit()
            income.id = cursor.lastrowid
            logger.info(f"Income source '{income.source}' created with ID {income.id}")
            return income
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating income: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def update(self, income: Income) -> None:
        """Updates an existing income entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE income
                SET source = ?, amount = ?, received_date = ?
                WHERE id = ?
                """,
                (
                    income.source,
                    income.amount,
                    income.received_date.strftime("%Y-%m-%d"),
                    income.id,
                ),
            )
            conn.commit()
            logger.info(f"Income ID {income.id} updated successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating income ID {income.id}: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def delete(self, income_id: int) -> bool:
        """Deletes an income entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Income ID {income_id} deleted successfully.")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting income ID {income_id}: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def find_by_id(self, income_id: int) -> Optional[Income]:
        """Finds an income entry by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM income WHERE id = ?", (income_id,))
            row = cursor.fetchone()
            if row:
                return Income(
                    id=row["id"],
                    source=row["source"],
                    amount=row["amount"],
                    received_date=row["received_date"],
                )
            return None
        finally:
            conn.close()

    def list_all(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_query: Optional[str] = None,
    ) -> List[Income]:
        """Lists income entries with optional date filters and search query."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM income WHERE 1=1"
        params = []

        if start_date is not None:
            query += " AND received_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))

        if end_date is not None:
            query += " AND received_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))

        if search_query is not None and search_query.strip():
            query += " AND source LIKE ?"
            params.append(f"%{search_query.strip()}%")

        query += " ORDER BY received_date DESC, id DESC"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Income(
                    id=row["id"],
                    source=row["source"],
                    amount=row["amount"],
                    received_date=row["received_date"],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def get_total_income(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> float:
        """Returns the total income in the specified date range."""
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT SUM(amount) FROM income WHERE 1=1"
        params = []
        if start_date is not None:
            query += " AND received_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
        if end_date is not None:
            query += " AND received_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0.0
        finally:
            conn.close()
