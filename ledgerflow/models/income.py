from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any


@dataclass
class Income:
    source: str
    amount: float
    received_date: date
    id: Optional[int] = None

    def save(self, repository) -> "Income":
        if self.id is not None:
            return self.update(repository)
        saved_income = repository.create(self)
        self.id = saved_income.id
        return self

    def update(self, repository) -> "Income":
        if self.id is None:
            raise ValueError("Cannot update an income without an ID. Save it first.")
        repository.update(self)
        return self

    def delete(self, repository) -> bool:
        if self.id is None:
            raise ValueError("Cannot delete an income without an ID.")
        return repository.delete(self.id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "amount": self.amount,
            "received_date": self.received_date,
        }

    def __post_init__(self):
        if isinstance(self.received_date, str):
            self.received_date = datetime.strptime(
                self.received_date, "%Y-%m-%d"
            ).date()
        if self.amount <= 0:
            raise ValueError("Income amount must be positive.")
