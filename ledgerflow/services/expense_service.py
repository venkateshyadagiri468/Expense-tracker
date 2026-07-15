from typing import List, Optional
from datetime import date
from ledgerflow.repositories.expense_repository import ExpenseRepository
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.models.expense import Expense
from ledgerflow.services.observer import EventManager
from ledgerflow.utils.validators import (
    validate_amount,
    validate_string,
    validate_payment_method,
)
from ledgerflow.utils.date_utils import parse_date
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class ExpenseService:
    def __init__(
        self,
        expense_repo: Optional[ExpenseRepository] = None,
        category_repo: Optional[CategoryRepository] = None,
        event_manager: Optional[EventManager] = None,
    ):
        self.expense_repo = expense_repo or ExpenseRepository()
        self.category_repo = category_repo or CategoryRepository()
        self.event_manager = event_manager or EventManager()

    def create_expense(
        self,
        title: str,
        amount: float,
        category_id: int,
        payment_method: str,
        expense_date: date,
        note: Optional[str] = None,
    ) -> Expense:
        """Validates inputs, saves the expense, and fires an event to observers."""
        title_clean = validate_string(title, name="Title")
        amount_clean = validate_amount(amount, name="Amount")
        payment_clean = validate_payment_method(payment_method)
        date_clean = parse_date(expense_date)

        # Verify category exists
        category = self.category_repo.find_by_id(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} does not exist.")

        expense = Expense(
            title=title_clean,
            amount=amount_clean,
            category_id=category_id,
            payment_method=payment_clean,
            expense_date=date_clean,
            note=note,
        )

        saved_expense = expense.save(self.expense_repo)

        # Notify budget observers or other listeners
        self.event_manager.publish("expense_created", saved_expense)

        return saved_expense

    def update_expense(
        self,
        expense_id: int,
        title: str,
        amount: float,
        category_id: int,
        payment_method: str,
        expense_date: date,
        note: Optional[str] = None,
    ) -> Expense:
        """Updates expense attributes and fires event."""
        # Find existing
        expense = self.expense_repo.find_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense with ID {expense_id} not found.")

        title_clean = validate_string(title, name="Title")
        amount_clean = validate_amount(amount, name="Amount")
        payment_clean = validate_payment_method(payment_method)
        date_clean = parse_date(expense_date)

        # Verify category exists
        category = self.category_repo.find_by_id(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} does not exist.")

        expense.title = title_clean
        expense.amount = amount_clean
        expense.category_id = category_id
        expense.payment_method = payment_clean
        expense.expense_date = date_clean
        expense.note = note

        expense.update(self.expense_repo)

        # Notify observers
        self.event_manager.publish("expense_updated", expense)

        return expense

    def delete_expense(self, expense_id: int) -> bool:
        """Deletes an expense record."""
        expense = self.expense_repo.find_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense with ID {expense_id} not found.")

        success = expense.delete(self.expense_repo)
        if success:
            # We can notify observers of an expense deletion to recalculate budgets if needed
            self.event_manager.publish("expense_deleted", expense)
        return success

    def find_expense(self, expense_id: int) -> Expense:
        """Finds an expense by ID."""
        expense = self.expense_repo.find_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense with ID {expense_id} not found.")
        return expense

    def list_expenses(
        self,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        payment_method: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Expense]:
        """Lists expenses based on search and filters."""
        return self.expense_repo.list_all(
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            search_query=search_query,
        )
