# campusflow/workflow.py
"""Business rules: create, view, assign, change status, and build the work queue."""
from dataclasses import asdict

from .tickets import (
    Ticket,
    calculate_priority,
    validate_affected_users,
    validate_category,
    validate_status,
    validate_title,
    validate_urgency,
)

# Allowed status moves. Anything not listed here is rejected.
ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},  # explicit reopen
}

# F5: which statuses appear in the work queue (see docs/design-decisions.md).
QUEUE_STATUSES = {"open"}

PRIORITY_WEIGHTS = {"critical": 1, "high": 2, "medium": 3, "low": 4}


class WorkflowEngine:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        # F7: reload on startup (raises ValueError if the file is corrupted)
        self.tickets = self.storage.load_tickets_from_json()

    # ---------- helpers ----------
    def _get_ticket(self, ticket_id):
        """Return the REAL stored ticket (internal use only)."""
        if not isinstance(ticket_id, str) or ticket_id not in self.tickets:
            raise KeyError(f"Operation Failed: Ticket ID '{ticket_id}' does not exist.")
        return self.tickets[ticket_id]

    def _save_or_undo(self, undo):
        """Save to disk; if saving fails, undo the in-memory change and re-raise."""
        try:
            self.storage.save_tickets_to_json(self.tickets)
        except OSError:
            undo()
            raise

    # ---------- F1 ----------
    def create_and_store_ticket(self, raw_user_inputs):
        title = validate_title(raw_user_inputs.get("title", ""))
        category = validate_category(raw_user_inputs.get("category", ""))
        urgency = validate_urgency(raw_user_inputs.get("urgency", ""))
        affected_users = validate_affected_users(raw_user_inputs.get("affected_users"))

        # Only generate an ID after every check has passed.
        next_id = self.storage.generate_next_sequential_id()
        ticket = Ticket(
            id=next_id,
            title=title,
            category=category,
            urgency=urgency,
            affected_users=affected_users,
            priority=calculate_priority(urgency, affected_users),
            status="open",
            assigned_to=None,
        )

        self.tickets[next_id] = asdict(ticket)

        def undo():
            self.tickets.pop(next_id, None)
            self.storage.release_id(next_id)

        self._save_or_undo(undo)
        return next_id

    # ---------- F2 ----------
    def get_single_ticket_by_id(self, ticket_id):
        return dict(self._get_ticket(ticket_id))

    def get_all_tickets_list(self):
        return [dict(t) for t in self.tickets.values()]

    # ---------- F3 ----------
    def assign_ticket_to_staff(self, ticket_id, staff_name):
        ticket = self._get_ticket(ticket_id)

        if not isinstance(staff_name, str) or staff_name.strip() == "":
            raise ValueError("Assignment Failed: Staff member name cannot be blank.")
        if ticket["status"] == "resolved":
            raise ValueError(
                "Assignment Failed: Cannot assign staff to a 'resolved' ticket. Reopen it first."
            )

        previous = ticket["assigned_to"]
        ticket["assigned_to"] = staff_name.strip()
        self._save_or_undo(lambda: ticket.update(assigned_to=previous))

    # ---------- F4 ----------
    def transition_ticket_status(self, ticket_id, target_status):
        ticket = self._get_ticket(ticket_id)
        current = ticket["status"]

        if not isinstance(target_status, str) or target_status.strip() == "":
            raise ValueError("Workflow Error: Target status cannot be empty.")
        target = validate_status(target_status)

        if target not in ALLOWED_TRANSITIONS[current]:
            if current == "resolved":
                raise ValueError(
                    "Workflow Error: A resolved ticket is locked. "
                    "It must be explicitly reopened to 'open' first."
                )
            raise ValueError(
                f"Workflow Error: Cannot transition from '{current}' to '{target}'. "
                f"Allowed next status: {sorted(ALLOWED_TRANSITIONS[current])}."
            )

        if target == "in_progress" and not ticket.get("assigned_to"):
            raise ValueError(
                "Workflow Error: Cannot move an unassigned ticket into 'in_progress'. "
                "Assign staff first."
            )

        ticket["status"] = target
        self._save_or_undo(lambda: ticket.update(status=current))

    # ---------- F5 ----------
    def get_sorted_work_queue(self):
        """Queue tickets ordered critical -> low, ties broken by earlier numeric ID."""
        queue = [t for t in self.tickets.values() if t["status"] in QUEUE_STATUSES]

        def sort_key(ticket):
            weight = PRIORITY_WEIGHTS.get(str(ticket.get("priority", "low")).lower(), 5)
            raw_id = str(ticket.get("id", "T0"))
            number = int(raw_id[1:]) if raw_id[1:].isdigit() else 0
            return (weight, number)

        return [dict(t) for t in sorted(queue, key=sort_key)]