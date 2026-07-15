from typing import Union

# Allowed Payment Methods
PAYMENT_METHODS = ["Cash", "Card", "UPI", "Bank Transfer"]


def validate_amount(amount: Union[int, float], name: str = "Amount") -> float:
    """Validates that a financial amount is a positive number."""
    try:
        val = float(amount)
    except (ValueError, TypeError):
        raise ValueError(f"{name} must be a number.")
    if val <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return val


def validate_string(
    val: str, min_len: int = 1, max_len: int = 255, name: str = "Field"
) -> str:
    """Validates that a string value is not empty and is within character constraints."""
    if not isinstance(val, str):
        raise ValueError(f"{name} must be a text value.")
    stripped = val.strip()
    if len(stripped) < min_len:
        raise ValueError(f"{name} cannot be empty.")
    if len(stripped) > max_len:
        raise ValueError(f"{name} exceeds maximum length of {max_len} characters.")
    return stripped


def validate_payment_method(method: str) -> str:
    """Validates and standardizes payment methods."""
    val = validate_string(method, name="Payment method")
    matched = [m for m in PAYMENT_METHODS if m.lower() == val.lower()]
    if not matched:
        raise ValueError(
            f"Invalid payment method. Allowed values are: {', '.join(PAYMENT_METHODS)}"
        )
    return matched[0]


def validate_alert_percentage(pct: int) -> int:
    """Validates that a percentage budget alert is between 1 and 100."""
    try:
        val = int(pct)
    except (ValueError, TypeError):
        raise ValueError("Alert percentage must be an integer.")
    if not (1 <= val <= 100):
        raise ValueError("Alert percentage must be between 1 and 100.")
    return val
