from typing import List, Optional
from datetime import date
from ledgerflow.repositories.income_repository import IncomeRepository
from ledgerflow.models.income import Income
from ledgerflow.utils.validators import validate_amount, validate_string
from ledgerflow.utils.date_utils import parse_date
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class IncomeService:
    def __init__(self, income_repo: Optional[IncomeRepository] = None):
        self.income_repo = income_repo or IncomeRepository()

    def add_income(self, source: str, amount: float, received_date: date) -> Income:
        """Adds a new income entry after validating input fields."""
        source_clean = validate_string(source, name="Source")
        amount_clean = validate_amount(amount, name="Amount")
        date_clean = parse_date(received_date)

        income = Income(
            source=source_clean, amount=amount_clean, received_date=date_clean
        )
        return income.save(self.income_repo)

    def update_income(
        self, income_id: int, source: str, amount: float, received_date: date
    ) -> Income:
        """Updates an existing income entry."""
        income = self.income_repo.find_by_id(income_id)
        if not income:
            raise ValueError(f"Income with ID {income_id} not found.")

        source_clean = validate_string(source, name="Source")
        amount_clean = validate_amount(amount, name="Amount")
        date_clean = parse_date(received_date)

        income.source = source_clean
        income.amount = amount_clean
        income.received_date = date_clean
        return income.save(self.income_repo)

    def delete_income(self, income_id: int) -> bool:
        """Deletes an income entry."""
        income = self.income_repo.find_by_id(income_id)
        if not income:
            raise ValueError(f"Income with ID {income_id} not found.")
        return income.delete(self.income_repo)

    def list_income(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_query: Optional[str] = None,
    ) -> List[Income]:
        """Lists income entries."""
        return self.income_repo.list_all(
            start_date=start_date, end_date=end_date, search_query=search_query
        )

    def total_income(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> float:
        """Returns aggregate income in specified range."""
        return self.income_repo.get_total_income(
            start_date=start_date, end_date=end_date
        )
