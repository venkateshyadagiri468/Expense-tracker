from typing import List, Optional
from ledgerflow.repositories.base_repository import BaseRepository
from ledgerflow.models.category import Category
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class CategoryRepository(BaseRepository):
    def create(self, category: Category) -> Category:
        """Inserts a new category into the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (name, icon, color) VALUES (?, ?, ?)",
                (category.name, category.icon, category.color),
            )
            conn.commit()
            category.id = cursor.lastrowid
            logger.info(f"Category '{category.name}' created with ID {category.id}")
            return category
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating category: {e}", exc_info=True)
            raise e
        finally:
            conn.close()

    def find_by_id(self, category_id: int) -> Optional[Category]:
        """Finds a category by its ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, icon, color FROM categories WHERE id = ?",
                (category_id,),
            )
            row = cursor.fetchone()
            if row:
                return Category(
                    id=row["id"], name=row["name"], icon=row["icon"], color=row["color"]
                )
            return None
        finally:
            conn.close()

    def find_by_name(self, name: str) -> Optional[Category]:
        """Finds a category by its unique name."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, icon, color FROM categories WHERE name = ?",
                (name.strip(),),
            )
            row = cursor.fetchone()
            if row:
                return Category(
                    id=row["id"], name=row["name"], icon=row["icon"], color=row["color"]
                )
            return None
        finally:
            conn.close()

    def list_all(self) -> List[Category]:
        """Lists all categories in the system."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, icon, color FROM categories ORDER BY name ASC"
            )
            rows = cursor.fetchall()
            return [
                Category(
                    id=row["id"], name=row["name"], icon=row["icon"], color=row["color"]
                )
                for row in rows
            ]
        finally:
            conn.close()

    def delete(self, category_id: int) -> bool:
        """Deletes a category if not referenced by any expenses (enforced by foreign keys)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Category ID {category_id} deleted successfully.")
            return success
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete category: {e}", exc_info=True)
            raise e
        finally:
            conn.close()
