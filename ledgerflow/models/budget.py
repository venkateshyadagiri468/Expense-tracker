from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Budget:
    category_id: int
    monthly_limit: float
    alert_percentage: int = 80
    spent: float = 0.0
    id: Optional[int] = None
    category_name: Optional[str] = None  # Helper for display

    def remaining(self) -> float:
        """Returns the remaining budget amount."""
        return max(0.0, self.monthly_limit - self.spent)

    def is_exceeded(self) -> bool:
        """Checks if the budget has been exceeded."""
        return self.spent >= self.monthly_limit

    def percentage(self) -> float:
        """Returns the percentage of the budget spent."""
        if self.monthly_limit <= 0:
            return 0.0
        return (self.spent / self.monthly_limit) * 100.0

    def is_near_limit(self) -> bool:
        """Checks if the spending has reached or exceeded the alert threshold percentage."""
        return self.percentage() >= self.alert_percentage

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category_id": self.category_id,
            "monthly_limit": self.monthly_limit,
            "alert_percentage": self.alert_percentage,
            "spent": self.spent,
        }

    def __post_init__(self):
        if self.monthly_limit <= 0:
            raise ValueError("Budget monthly limit must be positive.")
        if not (1 <= self.alert_percentage <= 100):
            raise ValueError("Budget alert percentage must be between 1 and 100.")
