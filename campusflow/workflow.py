# workflow.py

# Import only the core data struct from ticket
from .tickets import Ticket, calculate_priority

class WorkflowEngine:
    def __init__(self, storage_manager):
        self.storage = storage_manager
        # F7 Reload on startup
        self.tickets = self.storage.load_tickets_from_json()

    def create_and_store_ticket(self, raw_user_inputs):
        allowed_categories = {"Network", "Hardware", "Software", "Other"}
        allowed_urgencies = {"low", "medium", "high"}

        # 1. Extract and check Title
        title = raw_user_inputs.get("title", "")
        if title == "" or title.isspace():
            raise ValueError("Validation Failed: Title cannot be empty or blank spaces.")

        # 2. Case Normalization and check for Category (e.g., "network" -> "Network")
        category = str(raw_user_inputs.get("category", "")).strip().capitalize()
        if category not in allowed_categories:
            raise ValueError(f"Validation Failed: Allowed categories are {sorted(list(allowed_categories))}.")

        # 3. Case Normalization and check for Urgency (e.g., "HIGH" -> "high")
        urgency = str(raw_user_inputs.get("urgency", "")).strip().lower()
        if urgency not in allowed_urgencies:
            raise ValueError(f"Validation Failed: Allowed urgency levels are {sorted(list(allowed_urgencies))}.")

        # 4. Enforce positive whole integer rule for affected_users
        affected_users_raw = raw_user_inputs.get("affected_users")
        if isinstance(affected_users_raw, bool):
            raise ValueError("Validation Failed: affected_users cannot be a boolean value.")
            
        try:
            if isinstance(affected_users_raw, str) and "." in affected_users_raw:
                raise ValueError()
            affected_users = int(affected_users_raw)
            if isinstance(affected_users_raw, float):
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("Validation Failed: affected_users must be a positive whole integer (not text or decimal).")

        if affected_users <= 0:
            raise ValueError("Validation Failed: affected_users cannot be 0 or negative.")

        # 5. Automatically generate the next safe ID string
        next_id = self.storage.generate_next_sequential_id()
        
        # 1.3 Calculate priority exactly as specified by priority rules
        calculated_prio = calculate_priority(urgency, affected_users)

        # 6. Build the safe dictionary structure matching your required fields
        validated_ticket_dict = {
            "id": next_id,
            "title": title,
            "category": category,
            "urgency": urgency,
            "affected_users": affected_users,
            "priority": calculated_prio,
            "status": "open",
            "assigned_to": None
        }
        
        # 7. Commit to application memory state and write to disk
        self.tickets[next_id] = validated_ticket_dict
        self.storage.save_tickets_to_json(self.tickets)
        
        return next_id

    def get_single_ticket_by_id(self, ticket_id):
        if ticket_id not in self.tickets:
            raise KeyError(f"Operation Failed: Ticket ID '{ticket_id}' does not exist.")
        return self.tickets[ticket_id]

    def get_all_tickets_list(self):
        return list(self.tickets.values())

    def assign_ticket_to_staff(self, ticket_id, staff_name):
        ticket = self.get_single_ticket_by_id(ticket_id)

        if not staff_name or staff_name.isspace():
            raise ValueError("Assignment Failed: Staff member name cannot be blank.")
        
        if ticket["status"] == "resolved":
            raise ValueError("Assignment Failed: Cannot assign staff to a 'resolved' ticket. Reopen it first.")

        ticket["assigned_to"] = staff_name.strip()
        self.storage.save_tickets_to_json(self.tickets)

    def transition_ticket_status(self, ticket_id, target_status):
        ticket = self.get_single_ticket_by_id(ticket_id)
        current = ticket["status"]
        
        if not target_status or target_status.isspace():
            raise ValueError("Workflow Error: Target status cannot be empty.")
            
        target = target_status.strip().lower()
        
        allowed_statuses = {"open", "in_progress", "resolved"}
        if target not in allowed_statuses:
            raise ValueError(f"Workflow Error: Status must be one of {allowed_statuses}.")

        if current == "resolved" and target != "open":
            raise ValueError("Workflow Error: A resolved ticket is locked. It must be explicitly reopened to 'open' first.")

        if target == "in_progress":
            if not ticket.get("assigned_to"):
                raise ValueError("Workflow Error: Cannot move an unassigned ticket into 'in_progress'. Assign staff first.")
            if current != "open":
                raise ValueError(f"Workflow Error: Cannot transition directly from '{current}' to 'in_progress'.")

        if target == "resolved":
            if current != "in_progress":
                raise ValueError(f"Workflow Error: Cannot transition directly from '{current}' to 'resolved'. Complete 'in_progress' first.")

        ticket["status"] = target
        self.storage.save_tickets_to_json(self.tickets)

    def get_sorted_work_queue(self):
        unresolved_tickets = [t for t in self.tickets.values() if t["status"] != "resolved"]

        priority_weights = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }

        def work_queue_sorting_key(ticket_dict):
            prio_str = ticket_dict.get("priority", "low").lower()
            prio_weight = priority_weights.get(prio_str, 5)

            raw_id = ticket_dict.get("id", "T000")
            id_numeric_part = int(raw_id[1:]) if raw_id[1:].isdigit() else 0

            return (prio_weight, id_numeric_part)

        return sorted(unresolved_tickets, key=work_queue_sorting_key)
