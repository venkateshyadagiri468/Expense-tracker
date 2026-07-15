from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any


@dataclass
class Expense:
    title: str
    amount: float
    category_id: int
    payment_method: str
    expense_date: date
    note: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    category_name: Optional[str] = None  # Helper for display purposes

    def save(self, repository) -> "Expense":
        """Saves the current expense using the injected repository."""
        if self.id is not None:
            return self.update(repository)
        saved_expense = repository.create(self)
        self.id = saved_expense.id
        self.created_at = saved_expense.created_at
        return self

    def update(self, repository) -> "Expense":
        """Updates the current expense using the injected repository."""
        if self.id is None:
            raise ValueError("Cannot update an expense without an ID. Save it first.")
        repository.update(self)
        return self

    def delete(self, repository) -> bool:
        """Deletes the current expense using the injected repository."""
        if self.id is None:
            raise ValueError("Cannot delete an expense without an ID.")
        return repository.delete(self.id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category_id": self.category_id,
            "payment_method": self.payment_method,
            "expense_date": self.expense_date,
            "note": self.note,
            "created_at": self.created_at,
        }

    def __post_init__(self):
        if isinstance(self.expense_date, str):
            self.expense_date = datetime.strptime(self.expense_date, "%Y-%m-%d").date()
        if isinstance(self.created_at, str):
            self.created_at = datetime.strptime(self.created_at, "%Y-%m-%d %H:%M:%S")
        if self.amount <= 0:
            raise ValueError("Expense amount must be positive.")
