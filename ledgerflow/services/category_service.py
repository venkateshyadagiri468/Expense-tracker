from typing import List, Optional
import sqlite3
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.models.category import Category
from ledgerflow.utils.validators import validate_string
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class CategoryService:
    def __init__(self, category_repo: Optional[CategoryRepository] = None):
        self.category_repo = category_repo or CategoryRepository()

    def create_category(
        self, name: str, icon: Optional[str] = None, color: Optional[str] = None
    ) -> Category:
        """Creates a new category with input validation and uniqueness checks."""
        name_clean = validate_string(name, name="Category name")

        # Uniqueness check
        existing = self.category_repo.find_by_name(name_clean)
        if existing:
            raise ValueError(f"Category with name '{name_clean}' already exists.")

        category = Category(name=name_clean, icon=icon, color=color)
        return self.category_repo.create(category)

    def get_category_by_id(self, category_id: int) -> Category:
        """Fetches a category by ID or raises ValueError if not found."""
        category = self.category_repo.find_by_id(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} not found.")
        return category

    def list_all_categories(self) -> List[Category]:
        """Lists all categories ordered by name."""
        return self.category_repo.list_all()

    def delete_category(self, category_id: int) -> bool:
        """Deletes a category. Raises ValueError if category is in use by expenses."""
        try:
            return self.category_repo.delete(category_id)
        except sqlite3.IntegrityError:
            raise ValueError(
                "Cannot delete this category because it is in use by existing expenses."
            )
        except Exception as e:
            logger.error(f"Error in delete_category service: {e}")
            raise e
