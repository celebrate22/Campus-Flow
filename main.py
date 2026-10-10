# main.py
"""Command-line menu for CampusFlow. Run from the project root: python main.py"""
import sys

from campusflow.reports import generate_system_summary_report
from campusflow.storage import TicketStorage
from campusflow.workflow import WorkflowEngine

HANDLED_ERRORS = (KeyError, ValueError, OSError)


def error_text(err):
    """KeyError wraps its message in quotes; args[0] gives the plain text."""
    return str(err.args[0]) if isinstance(err, KeyError) and err.args else str(err)


def display_menu():
    print("\n" + "=" * 45)
    print("      CAMPUS HELP DESK TICKETING SYSTEM")
    print("=" * 45)
    print(" 1. Create Ticket [F1]")
    print(" 2. List All Tickets [F2]")
    print(" 3. View Single Ticket Details [F2]")
    print(" 4. Assign Ticket to Staff [F3]")
    print(" 5. Transition Ticket Status [F4]")
    print(" 6. View Sorted Work Queue [F5]")
    print(" 7. Generate Metrics Summary Report [F6]")
    print(" 8. Exit System")
    print("=" * 45)


def print_ticket_row(t):
    owner = t.get("assigned_to") or "Unassigned"
    print(
        f"[{t['id']}] {t['title'][:25]:<25} | Prio: {t['priority'].upper():<8} "
        f"| Status: {t['status'].upper():<11} | Owner: {owner}"
    )


def handle_create(engine):
    print("\n--- CREATE NEW TICKET ---")
    raw_inputs = {
        "title": input("Enter Ticket Title: "),
        "category": input("Enter Category (Network, Hardware, Software, Other): "),
        "urgency": input("Enter Urgency Level (low, medium, high): "),
        "affected_users": input("Enter Number of Affected Users: "),
    }
    new_id = engine.create_and_store_ticket(raw_inputs)
    print(f"\n[SUCCESS] Ticket created with unique ID: {new_id}")


def handle_list(engine):
    print("\n--- ALL REGISTERED TICKETS ---")
    tickets = engine.get_all_tickets_list()
    if not tickets:
        print("No tickets found.")
    for t in tickets:
        print_ticket_row(t)


def handle_view(engine):
    print("\n--- VIEW TICKET DETAILS ---")
    ticket_id = input("Enter Ticket ID (e.g., T001): ").strip().upper()
    t = engine.get_single_ticket_by_id(ticket_id)
    print("\n" + "-" * 40)
    print(f" Ticket ID       : {t['id']}")
    print(f" Title           : {t['title']}")
    print(f" Category        : {t['category']}")
    print(f" Urgency         : {t['urgency']}")
    print(f" Affected Users  : {t['affected_users']}")
    print(f" Priority        : {t['priority'].upper()}")
    print(f" Status          : {t['status'].upper()}")
    print(f" Assigned To     : {t['assigned_to'] or 'None'}")
    print("-" * 40)


def handle_assign(engine):
    print("\n--- ASSIGN TICKET ---")
    ticket_id = input("Enter Ticket ID to Assign: ").strip().upper()
    staff_name = input("Enter Staff Member Name: ")
    engine.assign_ticket_to_staff(ticket_id, staff_name)
    print(f"\n[SUCCESS] Ticket {ticket_id} assigned to '{staff_name.strip()}'.")


def handle_transition(engine):
    print("\n--- WORKFLOW TRANSITION ---")
    ticket_id = input("Enter Ticket ID: ").strip().upper()
    print("Target states: open | in_progress | resolved")
    target_status = input("Enter New Status: ")
    engine.transition_ticket_status(ticket_id, target_status)
    print(f"\n[SUCCESS] Ticket {ticket_id} is now '{target_status.strip().lower()}'.")


def handle_queue(engine):
    print("\n--- WORK QUEUE (PRIORITIZED) ---")
    queue = engine.get_sorted_work_queue()
    if not queue:
        print("The work queue is currently empty.")
    for t in queue:
        print_ticket_row(t)


def handle_report(engine):
    generate_system_summary_report(engine.get_all_tickets_list())


ACTIONS = {
    "1": handle_create,
    "2": handle_list,
    "3": handle_view,
    "4": handle_assign,
    "5": handle_transition,
    "6": handle_queue,
    "7": handle_report,
}


def main():
    try:
        engine = WorkflowEngine(TicketStorage())
    except (ValueError, OSError) as err:
        print(f"\nCRITICAL STARTUP ERROR:\n{err}")
        sys.exit(1)

    try:
        while True:
            display_menu()
            choice = input("Select an option (1-8): ").strip()

            if choice == "8":
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("\n[INVALID OPTION] Please type a number between 1 and 8.")
                continue
            try:
                action(engine)
            except HANDLED_ERRORS as err:
                print(f"\n[REJECTED] {error_text(err)}")
    except (KeyboardInterrupt, EOFError):
        print()

    print("\nGoodbye!")


if __name__ == "__main__":
    main()