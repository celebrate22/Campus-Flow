# campusflow/tickets.py
"""Ticket data shape, input validators and the priority engine.

Everything here is plain business logic: no input(), no print(), no file access.
That makes it easy to unit test.
"""
import re
from dataclasses import dataclass
from typing import Optional

ALLOWED_CATEGORIES = ("Network", "Hardware", "Software", "Other")
ALLOWED_URGENCIES = ("low", "medium", "high")
ALLOWED_STATUSES = ("open", "in_progress", "resolved")


@dataclass
class Ticket:
    id: str
    title: str
    category: str
    urgency: str
    affected_users: int
    priority: str
    status: str = "open"
    assigned_to: Optional[str] = None


def validate_title(title_text) -> str:
    """Return the trimmed title, or raise ValueError if it is blank or not text."""
    if not isinstance(title_text, str):
        raise ValueError("Validation Failed: Title must be text.")
    cleaned = title_text.strip()
    if cleaned == "":
        raise ValueError("Validation Failed: Title cannot be empty or just blank spaces.")
    return cleaned


def validate_category(category_text) -> str:
    """Normalize case ('network' -> 'Network') and check against allowed categories."""
    cleaned = str(category_text).strip().capitalize()
    if cleaned not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"Validation Failed: Category must be one of {list(ALLOWED_CATEGORIES)}."
        )
    return cleaned


def validate_urgency(urgency_text) -> str:
    """Normalize case ('HIGH' -> 'high') and check against allowed urgency levels."""
    cleaned = str(urgency_text).strip().lower()
    if cleaned not in ALLOWED_URGENCIES:
        raise ValueError(
            f"Validation Failed: Urgency must be one of {list(ALLOWED_URGENCIES)}."
        )
    return cleaned


def validate_status(status_text) -> str:
    """Normalize case and check against the allowed workflow states."""
    cleaned = str(status_text).strip().lower()
    if cleaned not in ALLOWED_STATUSES:
        raise ValueError(
            f"Validation Failed: Status must be one of {list(ALLOWED_STATUSES)}."
        )
    return cleaned


def validate_affected_users(users_input) -> int:
    """Return affected_users as a positive int.

    Rejects text, decimals (5.5, 5.0, "5.0"), booleans, zero and negatives.
    Whole-number strings such as "12" or " 12 " are accepted.
    """
    if isinstance(users_input, bool):
        raise ValueError("Validation Failed: affected_users cannot be a boolean value.")

    if isinstance(users_input, int):
        value = users_input
    elif isinstance(users_input, str) and re.fullmatch(r"[+-]?[0-9]+", users_input.strip()):
        value = int(users_input.strip())
    else:
        raise ValueError(
            "Validation Failed: affected_users must be a positive whole integer "
            "(not text or decimal)."
        )

    if value <= 0:
        raise ValueError("Validation Failed: affected_users cannot be 0 or negative.")
    return value


def calculate_priority(urgency: str, affected_users: int) -> str:
    """Apply the priority rules in order; the first match wins."""
    # RULE 1: high urgency AND 10 or more affected users -> critical
    if urgency == "high" and affected_users >= 10:
        return "critical"
    # RULE 2: high urgency OR 10 or more affected users -> high
    if urgency == "high" or affected_users >= 10:
        return "high"
    # RULE 3: medium urgency OR 3 or more affected users -> medium
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    # RULE 4: everything else -> low
    return "low"