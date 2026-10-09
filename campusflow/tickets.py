# campusflow/tickets.py
from dataclasses import dataclass

@dataclass
class Ticket:
    id: str
    title: str
    category: str
    urgency: str
    affected_users: int
    priority: str
    status: str
    assigned_to: str

def validate_title(title_text: str) -> None:
    """Validates that the title is not empty or just whitespace."""
    if title_text == "":
        raise ValueError("Validation Failed: Title cannot be empty.")
    if title_text.isspace():
        raise ValueError("Validation Failed: Title cannot be just blank spaces.")

def validate_status(status_text: str) -> None:
    """Validates that the status matches allowed workflow states."""
    allowed_statuses = {"open", "in_progress", "resolved"}
    if status_text not in allowed_statuses:
        raise ValueError(f"Validation Failed: Status must be one of {allowed_statuses}.")

def validate_affected_users(users_input) -> int:
    """
    Enforces that affected_users must be a positive integer.
    Rejects text strings, decimals, zeros, and negative numbers.
    """
    if isinstance(users_input, bool):
        raise ValueError("Validation Failed: affected_users cannot be a boolean value.")
        
    try:
        if isinstance(users_input, str) and "." in users_input:
            raise ValueError()
        value = int(users_input)
        if isinstance(users_input, float):
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("Validation Failed: affected_users must be a positive whole integer (not text or decimal).")

    if value <= 0:
        raise ValueError("Validation Failed: affected_users cannot be 0 or negative.")
        
    return value

def calculate_priority(urgency: str, affected_users: int) -> str:
    """
    Calculates and returns the ticket priority based on urgency and affected users.
    Rules are evaluated in sequential order; the first matching rule wins.
    """
    # RULE 1: high urgency AND 10 or more affected users -> critical
    if urgency == "high" and affected_users >= 10:
        return "critical"

    # RULE 2: high urgency OR 10 or more affected users -> high
    if urgency == "high" or affected_users >= 10:
        return "high"

    # RULE 3: medium urgency OR 3 or more affected users -> medium
    if urgency == "medium" or affected_users >= 3:
        return "medium"

    # RULE 4: all remaining valid tickets -> low
    return "low"
