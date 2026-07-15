from datetime import date
from typing import Dict, Any
from ledgerflow.services.expense_service import ExpenseService
from ledgerflow.services.income_service import IncomeService
from ledgerflow.services.budget_service import BudgetService
from ledgerflow.utils.date_utils import get_month_range


class DashboardController:
    def __init__(
        self,
        expense_service: ExpenseService,
        income_service: IncomeService,
        budget_service: BudgetService,
    ):
        self.expense_service = expense_service
        self.income_service = income_service
        self.budget_service = budget_service

    def get_dashboard_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Aggregates all components required to construct the LedgerFlow main dashboard."""
        start_date, end_date = get_month_range(year, month)

        # 1. Financial Balances
        expenses_list = self.expense_service.list_expenses(
            start_date=start_date, end_date=end_date
        )
        total_expenses = sum(e.amount for e in expenses_list)
        total_income = self.income_service.total_income(
            start_date=start_date, end_date=end_date
        )
        balance = total_income - total_expenses

        # 2. Top Categories
        category_breakdown = {}
        for e in expenses_list:
            cat_name = e.category_name or "Uncategorized"
            category_breakdown[cat_name] = (
                category_breakdown.get(cat_name, 0.0) + e.amount
            )

        top_categories = sorted(
            [{"name": k, "amount": v} for k, v in category_breakdown.items()],
            key=lambda x: x["amount"],
            reverse=True,
        )

        # 3. Monthly Budgets
        budgets = self.budget_service.list_all_budgets(year, month)

        # 4. Today's Transactions
        today = date.today()
        todays_expenses = self.expense_service.list_expenses(
            start_date=today, end_date=today
        )

        return {
            "balance": balance,
            "income": total_income,
            "expenses": total_expenses,
            "savings": balance,  # Savings is the surplus/balance
            "top_categories": top_categories,
            "budgets": budgets,
            "todays_expenses": todays_expenses,
            "month_name": start_date.strftime("%B"),
            "year": year,
        }
