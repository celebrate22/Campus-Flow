# main.py
import sys

# Update these lines to look inside the package folder:
from campusflow.storage import TicketStorage
from campusflow.workflow import WorkflowEngine
from campusflow.reports import generate_system_summary_report

# ... (the rest of your main.py code stays exactly the same) ...

def display_menu():
    """Prints the clear text interface menu options."""
    print("\n" + "=" * 45)
    print("      CAMPUS HELP DESK TICKETING SYSTEM      ")
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
    """Helper layout function to print out basic row summaries cleanly."""
    owner = t.get("assigned_to") if t.get("assigned_to") else "Unassigned"
    print(f"[{t['id']}] {t['title'][:25]:<25} | Prio: {t['priority'].upper():<8} | Status: {t['status'].upper():<11} | Owner: {owner}")

def main():
    # Initialize the persistence storage unit first
    # This captures corruption/malformed JSON flags immediately before structural entry
    try:
        storage = TicketStorage("tickets.json")
        engine = WorkflowEngine(storage)
    except ValueError as err:
        print(f"\nCRITICAL STARTUP ERROR:\n{err}")
        sys.exit(1)

    while True:
        display_menu()
        choice = input("Select an option (1-8): ").strip()

        if choice == "1":
            print("\n--- CREATE NEW TICKET ---")
            title = input("Enter Ticket Title: ")
            category = input("Enter Category (Network, Hardware, Software, Other): ")
            urgency = input("Enter Urgency Level (low, medium, high): ")
            affected_users_raw = input("Enter Number of Affected Users: ")

            # Prepare the structural raw map block
            raw_inputs = {
                "title": title,
                "category": category,
                "urgency": urgency,
                "affected_users": affected_users_raw
            }

            try:
                # F1 Create, validate, calculate priority, assign unique sequential ID, and save
                new_id = engine.create_and_store_ticket(raw_inputs)
                print(f"\n[SUCCESS] Ticket created successfully with unique ID: {new_id}")
            except ValueError as err:
                print(f"\n[REJECTED] {err}")

        elif choice == "2":
            print("\n--- ALL REGISTERED TICKETS ---")
            tickets = engine.get_all_tickets_list()
            if not tickets:
                print("No tickets found in the tracking registry bank.")
            else:
                for t in tickets:
                    print_ticket_row(t)

        elif choice == "3":
            print("\n--- VIEW TICKET DETAILS ---")
            ticket_id = input("Enter Ticket ID (e.g., T001): ").strip().upper()
            try:
                t = engine.get_single_ticket_by_id(ticket_id)
                print("\n" + "-"*40)
                print(f" Ticket Identifier : {t['id']}")
                print(f" Title             : {t['title']}")
                print(f" Category          : {t['category']}")
                print(f" Urgency Level     : {t['urgency']}")
                print(f" Affected Users    : {t['affected_users']}")
                print(f" Calculated Prio   : {t['priority'].upper()}")
                print(f" Workflow Status   : {t['status'].upper()}")
                print(f" Assigned Staff    : {t['assigned_to'] if t['assigned_to'] else 'None'}")
                print("-"*40)
            except KeyError as err:
                print(f"\n[ERROR] {err.args[0]}")

        elif choice == "4":
            print("\n--- ASSIGN TICKET ---")
            ticket_id = input("Enter Ticket ID to Assign: ").strip().upper()
            staff_name = input("Enter Staff Member Name: ")
            try:
                engine.assign_ticket_to_staff(ticket_id, staff_name)
                print(f"\n[SUCCESS] Ticket {ticket_id} has been safely assigned to '{staff_name.strip()}'.")
            except (KeyError, ValueError) as err:
                # Intercepts unknown ticket IDs or invalid text inputs safely
                # Avoiding positional arg crashes by casting to string
                print(f"\n[REJECTED] {str(err).strip(\"'\")}")

        elif choice == "5":
            print("\n--- WORKFLOW TRANSITION ---")
            ticket_id = input("Enter Ticket ID to Progress: ").strip().upper()
            print("Target States: open | in_progress | resolved")
            target_status = input("Enter New Target Status: ")
            try:
                engine.transition_ticket_status(ticket_id, target_status)
                print(f"\n[SUCCESS] Ticket {ticket_id} workflow shifted to '{target_status.strip().lower()}'.")
            except (KeyError, ValueError) as err:
                print(f"\n[REJECTED] {str(err).strip(\"'\")}")

        elif choice == "6":
            print("\n--- WORK QUEUE (PRIORITIZED) ---")
            # F5 Filters out resolved files, groups critical -> low, and tie-breaks via earlier IDs
            queue = engine.get_sorted_work_queue()
            if not queue:
                print("The active operations work queue is currently empty.")
            else:
                for t in queue:
                    print_ticket_row(t)

        elif choice == "7":
            # F6 Compiles totals and maps breakdowns without dividing errors on zero states
            tickets = engine.get_all_tickets_list()
            generate_system_summary_report(tickets)

        elif choice == choice == "8":
            print("\nShutting down help desk core database connections safely... Goodbye!")
            break

        else:
            print("\n[INVALID OPTION] Please type a numeric selection between 1 and 8.")

if __name__ == "__main__":
    main()
