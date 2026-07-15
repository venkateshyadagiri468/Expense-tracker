from typing import List, Optional, Dict, Any
from datetime import date
from ledgerflow.services.expense_service import ExpenseService
from ledgerflow.models.expense import Expense


class ExpenseController:
    def __init__(self, expense_service: ExpenseService):
        self.expense_service = expense_service

    def add_expense(
        self,
        title: str,
        amount: float,
        category_id: int,
        payment_method: str,
        expense_date: str,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Routes expense creation with error boundary handling."""
        try:
            expense = self.expense_service.create_expense(
                title=title,
                amount=amount,
                category_id=category_id,
                payment_method=payment_method,
                expense_date=expense_date,
                note=note,
            )
            return {"success": True, "data": expense, "error": None}
        except ValueError as ve:
            return {"success": False, "data": None, "error": str(ve)}
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"An unexpected error occurred: {e}",
            }

    def update_expense(
        self,
        expense_id: int,
        title: str,
        amount: float,
        category_id: int,
        payment_method: str,
        expense_date: str,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Routes expense updates."""
        try:
            expense = self.expense_service.update_expense(
                expense_id=expense_id,
                title=title,
                amount=amount,
                category_id=category_id,
                payment_method=payment_method,
                expense_date=expense_date,
                note=note,
            )
            return {"success": True, "data": expense, "error": None}
        except ValueError as ve:
            return {"success": False, "data": None, "error": str(ve)}
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"An unexpected error occurred: {e}",
            }

    def delete_expense(self, expense_id: int) -> Dict[str, Any]:
        """Routes expense deletion."""
        try:
            success = self.expense_service.delete_expense(expense_id)
            return {"success": success, "error": None}
        except ValueError as ve:
            return {"success": False, "error": str(ve)}
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {e}"}

    def list_expenses(
        self,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        payment_method: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Expense]:
        """Lists expenses using parameters."""
        return self.expense_service.list_expenses(
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            payment_method=payment_method,
            search_query=search_query,
        )

    def get_expense(self, expense_id: int) -> Dict[str, Any]:
        try:
            expense = self.expense_service.find_expense(expense_id)
            return {"success": True, "data": expense, "error": None}
        except ValueError as ve:
            return {"success": False, "data": None, "error": str(ve)}
