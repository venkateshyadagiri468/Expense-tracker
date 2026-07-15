from typing import List, Optional, Dict, Any
from datetime import date
from ledgerflow.services.income_service import IncomeService
from ledgerflow.models.income import Income


class IncomeController:
    def __init__(self, income_service: IncomeService):
        self.income_service = income_service

    def add_income(
        self, source: str, amount: float, received_date: str
    ) -> Dict[str, Any]:
        """Routes income creation with error boundary handling."""
        try:
            income = self.income_service.add_income(
                source=source, amount=amount, received_date=received_date
            )
            return {"success": True, "data": income, "error": None}
        except ValueError as ve:
            return {"success": False, "data": None, "error": str(ve)}
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"An unexpected error occurred: {e}",
            }

    def update_income(
        self, income_id: int, source: str, amount: float, received_date: str
    ) -> Dict[str, Any]:
        """Routes income updates."""
        try:
            income = self.income_service.update_income(
                income_id=income_id,
                source=source,
                amount=amount,
                received_date=received_date,
            )
            return {"success": True, "data": income, "error": None}
        except ValueError as ve:
            return {"success": False, "data": None, "error": str(ve)}
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"An unexpected error occurred: {e}",
            }

    def delete_income(self, income_id: int) -> Dict[str, Any]:
        """Routes income deletion."""
        try:
            success = self.income_service.delete_income(income_id)
            return {"success": success, "error": None}
        except ValueError as ve:
            return {"success": False, "error": str(ve)}
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {e}"}

    def list_incomes(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_query: Optional[str] = None,
    ) -> List[Income]:
        """Lists incomes."""
        return self.income_service.list_income(
            start_date=start_date, end_date=end_date, search_query=search_query
        )
