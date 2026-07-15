from datetime import date
from ledgerflow.services.expense_service import ExpenseService
from ledgerflow.services.income_service import IncomeService
from ledgerflow.services.report_service import ReportService
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.repositories.expense_repository import ExpenseRepository
from ledgerflow.repositories.income_repository import IncomeRepository


def test_financial_reports():
    cat_repo = CategoryRepository()
    exp_repo = ExpenseRepository()
    inc_repo = IncomeRepository()

    exp_service = ExpenseService(exp_repo, cat_repo)
    inc_service = IncomeService(inc_repo)
    report_service = ReportService(exp_repo, inc_repo)

    food_cat = cat_repo.find_by_name("Food")
    travel_cat = cat_repo.find_by_name("Travel")

    # Add income
    inc_service.add_income("Salary", 10000.0, date.today())

    # Add expenses
    exp_service.create_expense("Lunch", 200.0, food_cat.id, "Cash", date.today())
    exp_service.create_expense("Uber", 300.0, travel_cat.id, "Card", date.today())

    # Generate daily report
    report = report_service.get_daily_report(date.today())

    assert report["total_income"] == 10000.0
    assert report["total_expense"] == 500.0
    assert report["savings"] == 9500.0
    assert len(report["expenses"]) == 2
    assert report["category_breakdown"]["Food"] == 200.0
    assert report["category_breakdown"]["Travel"] == 300.0
    assert report["payment_breakdown"]["Cash"] == 200.0
    assert report["payment_breakdown"]["Card"] == 300.0
