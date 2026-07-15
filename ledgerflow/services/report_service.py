from typing import Dict, Any, List
from datetime import date
from ledgerflow.repositories.expense_repository import ExpenseRepository
from ledgerflow.repositories.income_repository import IncomeRepository
from ledgerflow.utils.date_utils import (
    get_month_range,
)


class ReportService:
    def __init__(
        self,
        expense_repo: ExpenseRepository = None,
        income_repo: IncomeRepository = None,
    ):
        self.expense_repo = expense_repo or ExpenseRepository()
        self.income_repo = income_repo or IncomeRepository()

    def get_summary_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generates general summary report for a given date range."""
        expenses = self.expense_repo.list_all(start_date=start_date, end_date=end_date)
        incomes = self.income_repo.list_all(start_date=start_date, end_date=end_date)

        total_expense = sum(e.amount for e in expenses)
        total_income = sum(i.amount for i in incomes)
        savings = total_income - total_expense

        # Category breakdown
        category_breakdown = {}
        for e in expenses:
            cat_name = e.category_name or "Uncategorized"
            category_breakdown[cat_name] = (
                category_breakdown.get(cat_name, 0.0) + e.amount
            )

        # Payment method breakdown
        payment_breakdown = {}
        for e in expenses:
            payment_breakdown[e.payment_method] = (
                payment_breakdown.get(e.payment_method, 0.0) + e.amount
            )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income,
            "total_expense": total_expense,
            "savings": savings,
            "expenses": expenses,
            "incomes": incomes,
            "category_breakdown": category_breakdown,
            "payment_breakdown": payment_breakdown,
        }

    def get_daily_report(self, target_date: date = None) -> Dict[str, Any]:
        """Generates daily income vs. expense report."""
        if target_date is None:
            target_date = date.today()
        return self.get_summary_report(target_date, target_date)

    def get_weekly_report(self, target_date: date = None) -> Dict[str, Any]:
        """Generates weekly report (Monday to Sunday) containing target_date."""
        if target_date is None:
            target_date = date.today()
        # Find Monday of that week
        monday = target_date - date.resolution * target_date.weekday()
        sunday = monday + date.resolution * 6
        return self.get_summary_report(monday, sunday)

    def get_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Generates monthly report."""
        start_date, end_date = get_month_range(year, month)
        return self.get_summary_report(start_date, end_date)

    def get_yearly_report(self, year: int) -> Dict[str, Any]:
        """Generates yearly report."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return self.get_summary_report(start_date, end_date)

    def get_cash_flow_report(self, year: int) -> List[Dict[str, Any]]:
        """Generates monthly cash flow report for the entire year."""
        cash_flow = []
        for month in range(1, 13):
            start_date, end_date = get_month_range(year, month)
            expenses = self.expense_repo.list_all(
                start_date=start_date, end_date=end_date
            )
            incomes = self.income_repo.list_all(
                start_date=start_date, end_date=end_date
            )

            total_expense = sum(e.amount for e in expenses)
            total_income = sum(i.amount for i in incomes)
            net_savings = total_income - total_expense

            cash_flow.append(
                {
                    "month": month,
                    "month_name": date(year, month, 1).strftime("%B"),
                    "income": total_income,
                    "expense": total_expense,
                    "net_savings": net_savings,
                }
            )
        return cash_flow
