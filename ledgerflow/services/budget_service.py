from typing import List, Optional
from datetime import date
from ledgerflow.repositories.budget_repository import BudgetRepository
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.models.budget import Budget
from ledgerflow.services.observer import Observer, EventManager
from ledgerflow.utils.validators import validate_amount, validate_alert_percentage
from ledgerflow.utils.logger import get_logger

logger = get_logger(__name__)


class BudgetService(Observer):
    def __init__(
        self,
        budget_repo: Optional[BudgetRepository] = None,
        category_repo: Optional[CategoryRepository] = None,
        event_manager: Optional[EventManager] = None,
    ):
        self.budget_repo = budget_repo or BudgetRepository()
        self.category_repo = category_repo or CategoryRepository()
        self.event_manager = event_manager

        # Buffer to keep active warnings/alerts for user visibility
        self.active_alerts: List[str] = []

        # Auto-subscribe if event manager is provided
        if self.event_manager:
            self.event_manager.subscribe("expense_created", self)
            self.event_manager.subscribe("expense_updated", self)

    def set_budget(
        self, category_id: int, monthly_limit: float, alert_percentage: int = 80
    ) -> Budget:
        """Sets or updates a monthly category budget."""
        limit_clean = validate_amount(monthly_limit, name="Budget limit")
        pct_clean = validate_alert_percentage(alert_percentage)

        # Check category existence
        category = self.category_repo.find_by_id(category_id)
        if not category:
            raise ValueError(f"Category with ID {category_id} does not exist.")

        today = date.today()
        # Check if budget already exists for this category
        existing = self.budget_repo.find_by_category_id(
            category_id, today.year, today.month
        )
        if existing:
            existing.monthly_limit = limit_clean
            existing.alert_percentage = pct_clean
            self.budget_repo.update(existing)
            logger.info(
                f"Updated budget limit for category ID {category_id} to {limit_clean}"
            )
            return existing
        else:
            budget = Budget(
                category_id=category_id,
                monthly_limit=limit_clean,
                alert_percentage=pct_clean,
            )
            return self.budget_repo.create(budget)

    def delete_budget(self, budget_id: int) -> bool:
        """Deletes a budget."""
        return self.budget_repo.delete(budget_id)

    def get_budget_by_category(
        self, category_id: int, year: int, month: int
    ) -> Optional[Budget]:
        """Gets category budget details for a month."""
        return self.budget_repo.find_by_category_id(category_id, year, month)

    def list_all_budgets(self, year: int, month: int) -> List[Budget]:
        """Lists all budgets for a given month and year."""
        return self.budget_repo.list_all(year, month)

    def get_alerts(self, clear: bool = True) -> List[str]:
        """Returns and optionally clears all accumulated budget alerts."""
        alerts = list(self.active_alerts)
        if clear:
            self.active_alerts.clear()
        return alerts

    def update(self, event: str, data: any) -> None:
        """Fired by EventManager when an expense is created or updated."""
        expense = data
        if not expense or not hasattr(expense, "category_id"):
            return

        # Check budget for the month the expense was placed in
        expense_date = expense.expense_date
        budget = self.budget_repo.find_by_category_id(
            expense.category_id, expense_date.year, expense_date.month
        )

        if budget:
            percentage = budget.percentage()
            category_name = budget.category_name or f"ID {budget.category_id}"

            # Check exceeded limit
            if budget.is_exceeded():
                alert_msg = (
                    f"🚨 [bold red]BUDGET EXCEEDED[/bold red]: Category '{category_name}' has exceeded "
                    f"its limit of ₹{budget.monthly_limit:.2f}! Total Spent: ₹{budget.spent:.2f}"
                )
                self.active_alerts.append(alert_msg)
                logger.warning(
                    f"Budget exceeded for category {category_name}: {budget.spent}/{budget.monthly_limit}"
                )
            # Check alert percentage threshold
            elif budget.is_near_limit():
                alert_msg = (
                    f"⚠️ [bold yellow]BUDGET WARNING[/bold yellow]: Category '{category_name}' spending "
                    f"has reached {percentage:.1f}% of its limit (₹{budget.spent:.2f} / ₹{budget.monthly_limit:.2f})"
                )
                self.active_alerts.append(alert_msg)
                logger.info(
                    f"Budget warning for category {category_name}: {percentage:.1f}% reached"
                )
