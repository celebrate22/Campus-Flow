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

def validate_ticket(ticket: Ticket) -> bool:
    # 1. Validate that the title is empty or just whitespace
    if ticket.title == "":
        raise ValueError("Validation Failed: Title cannot be empty.")
        
    if ticket.title.isspace():
        raise ValueError("Validation Failed: Title cannot be just blank spaces.")
        
    # 2. Validate that status is empty or just whitespace
    if ticket.status == "":
        raise ValueError("Validation Failed: Status cannot be empty.")
        
    if ticket.status.isspace():
        raise ValueError("Validation Failed: Status cannot be just blank spaces.")

    # 3. Reject if affected_users is 0 (or less)
    if ticket.affected_users <= 0:
        raise ValueError("Validation Failed: affected_users cannot be 0 or nagative.")
   
    return True
