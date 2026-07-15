from typing import List, Optional, Dict
from datetime import date
from ledgerflow.repositories.base_repository import BaseRepository
from ledgerflow.models.expense import Expense
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class ExpenseRepository(BaseRepository):
    def create(self, expense: Expense) -> Expense:
        """Saves a new expense and populates auto-generated database columns."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO expenses (title, amount, category_id, payment_method, expense_date, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    expense.title,
                    expense.amount,
                    expense.category_id,
                    expense.payment_method,
                    expense.expense_date.strftime("%Y-%m-%d"),
                    expense.note,
                ),
            )
            conn.commit()
            expense.id = cursor.lastrowid

            # Fetch created_at
            cursor.execute(
                "SELECT created_at FROM expenses WHERE id = ?", (expense.id,)
            )
            row = cursor.fetchone()
            expense.created_at = row["created_at"]

            logger.info(f"Expense '{expense.title}' created with ID {expense.id}")
            return expense
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating expense: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def update(self, expense: Expense) -> None:
        """Updates an existing expense in the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE expenses
                SET title = ?, amount = ?, category_id = ?, payment_method = ?, expense_date = ?, note = ?
                WHERE id = ?
                """,
                (
                    expense.title,
                    expense.amount,
                    expense.category_id,
                    expense.payment_method,
                    expense.expense_date.strftime("%Y-%m-%d"),
                    expense.note,
                    expense.id,
                ),
            )
            conn.commit()
            logger.info(f"Expense ID {expense.id} updated successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating expense ID {expense.id}: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def delete(self, expense_id: int) -> bool:
        """Deletes an expense from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Expense ID {expense_id} deleted successfully.")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting expense ID {expense_id}: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def find_by_id(self, expense_id: int) -> Optional[Expense]:
        """Finds an expense by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT e.*, c.name as category_name
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.id = ?
                """,
                (expense_id,),
            )
            row = cursor.fetchone()
            if row:
                return Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    category_id=row["category_id"],
                    payment_method=row["payment_method"],
                    expense_date=row["expense_date"],
                    note=row["note"],
                    created_at=row["created_at"],
                    category_name=row["category_name"],
                )
            return None
        finally:
            conn.close()

    def list_all(
        self,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        payment_method: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Expense]:
        """Lists expenses based on various filter options."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT e.*, c.name as category_name
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE 1=1
        """
        params = []

        if category_id is not None:
            query += " AND e.category_id = ?"
            params.append(category_id)

        if start_date is not None:
            query += " AND e.expense_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))

        if end_date is not None:
            query += " AND e.expense_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))

        if payment_method is not None:
            query += " AND e.payment_method = ?"
            params.append(payment_method)

        if search_query is not None and search_query.strip():
            query += " AND (e.title LIKE ? OR e.note LIKE ?)"
            like_str = f"%{search_query.strip()}%"
            params.extend([like_str, like_str])

        query += " ORDER BY e.expense_date DESC, e.id DESC"

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Expense(
                    id=row["id"],
                    title=row["title"],
                    amount=row["amount"],
                    category_id=row["category_id"],
                    payment_method=row["payment_method"],
                    expense_date=row["expense_date"],
                    note=row["note"],
                    created_at=row["created_at"],
                    category_name=row["category_name"],
                )
                for row in rows
            ]
        finally:
            conn.close()

    def get_monthly_spending_by_category(
        self, year: int, month: int
    ) -> Dict[str, float]:
        """Calculates total spending for each category in the specified month."""
        conn = self.get_connection()
        cursor = conn.cursor()
        # End date logic for SQLite: standard comparison or date functions
        query = """
            SELECT c.name, SUM(e.amount) as total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE strftime('%Y', e.expense_date) = ? AND strftime('%m', e.expense_date) = ?
            GROUP BY c.name
        """
        try:
            cursor.execute(query, (f"{year:04d}", f"{month:02d}"))
            return {row["name"]: row["total"] for row in cursor.fetchall()}
        finally:
            conn.close()
