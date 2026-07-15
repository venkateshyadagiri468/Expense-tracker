import pytest
from datetime import date
from ledgerflow.services.expense_service import ExpenseService
from ledgerflow.services.category_service import CategoryService
from ledgerflow.repositories.expense_repository import ExpenseRepository
from ledgerflow.repositories.category_repository import CategoryRepository
from ledgerflow.services.observer import EventManager


def test_create_valid_expense():
    event_mgr = EventManager()
    cat_repo = CategoryRepository()
    exp_repo = ExpenseRepository()

    cat_service = CategoryService(cat_repo)
    exp_service = ExpenseService(exp_repo, cat_repo, event_mgr)

    # Pre-condition: Seeding has occurred, so 'Food' category exists
    cats = cat_service.list_all_categories()
    food_cat = next(c for c in cats if c.name == "Food")

    # Create expense
    expense = exp_service.create_expense(
        title="Lunch",
        amount=150.0,
        category_id=food_cat.id,
        payment_method="UPI",
        expense_date=date.today(),
        note="Tacos",
    )

    assert expense.id is not None
    assert expense.title == "Lunch"
    assert expense.amount == 150.0
    assert expense.category_id == food_cat.id

    # Query database to check persistence
    fetched = exp_service.find_expense(expense.id)
    assert fetched.title == "Lunch"


def test_create_invalid_amount_raises_error():
    cat_repo = CategoryRepository()
    exp_repo = ExpenseRepository()
    exp_service = ExpenseService(exp_repo, cat_repo)

    food_cat = cat_repo.find_by_name("Food")

    with pytest.raises(ValueError, match="Amount must be greater than zero"):
        exp_service.create_expense(
            title="Lunch",
            amount=-50.0,
            category_id=food_cat.id,
            payment_method="Card",
            expense_date=date.today(),
        )


def test_create_nonexistent_category_raises_error():
    exp_service = ExpenseService()

    with pytest.raises(ValueError, match="Category with ID 99999 does not exist"):
        exp_service.create_expense(
            title="Uber",
            amount=350.0,
            category_id=99999,
            payment_method="Cash",
            expense_date=date.today(),
        )
