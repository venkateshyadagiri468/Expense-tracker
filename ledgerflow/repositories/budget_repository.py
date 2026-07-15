from typing import List, Optional
from ledgerflow.repositories.base_repository import BaseRepository
from ledgerflow.models.budget import Budget
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class BudgetRepository(BaseRepository):
    def create(self, budget: Budget) -> Budget:
        """Saves a new budget limit."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO budgets (category_id, monthly_limit, alert_percentage)
                VALUES (?, ?, ?)
                """,
                (budget.category_id, budget.monthly_limit, budget.alert_percentage),
            )
            conn.commit()
            budget.id = cursor.lastrowid
            logger.info(
                f"Budget created with ID {budget.id} for category ID {budget.category_id}"
            )
            return budget
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating budget: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def update(self, budget: Budget) -> None:
        """Updates an existing budget limit."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE budgets
                SET monthly_limit = ?, alert_percentage = ?
                WHERE id = ?
                """,
                (budget.monthly_limit, budget.alert_percentage, budget.id),
            )
            conn.commit()
            logger.info(f"Budget ID {budget.id} updated successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating budget ID {budget.id}: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def delete(self, budget_id: int) -> bool:
        """Deletes a budget limit."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Budget ID {budget_id} deleted successfully.")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting budget ID {budget_id}: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def find_by_id(self, budget_id: int, year: int, month: int) -> Optional[Budget]:
        """Finds a budget by ID, computing spent amount for the specified month/year."""
        conn = self.get_connection()
        cursor = conn.cursor()
        month_str = f"{year:04d}-{month:02d}"

        query = """
            SELECT b.*, c.name as category_name,
                   COALESCE((
                       SELECT SUM(amount)
                       FROM expenses
                       WHERE category_id = b.category_id
                         AND strftime('%Y-%m', expense_date) = ?
                   ), 0.0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.id = ?
        """
        try:
            cursor.execute(query, (month_str, budget_id))
            row = cursor.fetchone()
            if row:
                return Budget(
                    id=row["id"],
                    category_id=row["category_id"],
                    monthly_limit=row["monthly_limit"],
                    alert_percentage=row["alert_percentage"],
                    spent=row["spent"],
                    category_name=row["category_name"],
                )
            return None
        finally:
            conn.close()

    def find_by_category_id(
        self, category_id: int, year: int, month: int
    ) -> Optional[Budget]:
        """Finds a budget by category ID, computing spent amount for the specified month/year."""
        conn = self.get_connection()
        cursor = conn.cursor()
        month_str = f"{year:04d}-{month:02d}"

        query = """
            SELECT b.*, c.name as category_name,
                   COALESCE((
                       SELECT SUM(amount)
                       FROM expenses
                       WHERE category_id = b.category_id
                         AND strftime('%Y-%m', expense_date) = ?
                   ), 0.0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.category_id = ?
        """
        try:
            cursor.execute(query, (month_str, category_id))
            row = cursor.fetchone()
            if row:
                return Budget(
                    id=row["id"],
                    category_id=row["category_id"],
                    monthly_limit=row["monthly_limit"],
                    alert_percentage=row["alert_percentage"],
                    spent=row["spent"],
                    category_name=row["category_name"],
                )
            return None
        finally:
            conn.close()

    def list_all(self, year: int, month: int) -> List[Budget]:
        """Lists all budgets and calculates the spent amount in the given month/year."""
        conn = self.get_connection()
        cursor = conn.cursor()
        month_str = f"{year:04d}-{month:02d}"

        query = """
            SELECT b.*, c.name as category_name,
                   COALESCE((
                       SELECT SUM(amount)
                       FROM expenses
                       WHERE category_id = b.category_id
                         AND strftime('%Y-%m', expense_date) = ?
                   ), 0.0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            ORDER BY c.name ASC
        """
        try:
            cursor.execute(query, (month_str,))
            rows = cursor.fetchall()
            return [
                Budget(
                    id=row["id"],
                    category_id=row["category_id"],
                    monthly_limit=row["monthly_limit"],
                    alert_percentage=row["alert_percentage"],
                    spent=row["spent"],
                    category_name=row["category_name"],
                )
                for row in rows
            ]
        finally:
            conn.close()
