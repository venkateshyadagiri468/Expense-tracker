from datetime import date
from ledgerflow.services.expense_service import ExpenseService
from ledgerflow.services.budget_service import BudgetService
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.repositories.expense_repository import ExpenseRepository
from ledgerflow.repositories.budget_repository import BudgetRepository
from ledgerflow.services.observer import EventManager


def test_set_and_fetch_budget():
    budget_repo = BudgetRepository()
    cat_repo = CategoryRepository()
    budget_service = BudgetService(budget_repo, cat_repo)

    food_cat = cat_repo.find_by_name("Food")

    # Set budget
    budget = budget_service.set_budget(
        category_id=food_cat.id, monthly_limit=5000.0, alert_percentage=75
    )

    assert budget.id is not None
    assert budget.monthly_limit == 5000.0
    assert budget.alert_percentage == 75

    # Fetch budget
    today = date.today()
    fetched = budget_service.get_budget_by_category(
        food_cat.id, today.year, today.month
    )
    assert fetched is not None
    assert fetched.monthly_limit == 5000.0


def test_observer_alert_on_limit_exceeded():
    event_mgr = EventManager()
    cat_repo = CategoryRepository()
    exp_repo = ExpenseRepository()
    budget_repo = BudgetRepository()

    # Create services and inject event manager
    exp_service = ExpenseService(exp_repo, cat_repo, event_mgr)
    budget_service = BudgetService(budget_repo, cat_repo, event_mgr)

    food_cat = cat_repo.find_by_name("Food")

    # Set limit of ₹1000 with alert threshold of 80%
    budget_service.set_budget(
        category_id=food_cat.id, monthly_limit=1000.0, alert_percentage=80
    )

    # Trigger safe expense (₹500 -> 50% limit)
    exp_service.create_expense("Groceries", 500.0, food_cat.id, "Cash", date.today())
    assert len(budget_service.get_alerts(clear=True)) == 0  # No alerts

    # Trigger warning expense (₹300 more -> total ₹800 -> 80% threshold reached)
    exp_service.create_expense("Snacks", 300.0, food_cat.id, "UPI", date.today())
    alerts = budget_service.get_alerts(clear=True)
    assert len(alerts) == 1
    assert "BUDGET WARNING" in alerts[0]

    # Trigger exceeded expense (₹300 more -> total ₹1100 -> exceeded limit)
    exp_service.create_expense("Dinner", 300.0, food_cat.id, "Card", date.today())
    alerts = budget_service.get_alerts(clear=True)
    assert len(alerts) == 1
    assert "BUDGET EXCEEDED" in alerts[0]
