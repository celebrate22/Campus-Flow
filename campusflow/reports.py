# reports.py

def generate_system_summary_report(all_tickets_list):
    """
    F6 — REPORTS: Calculates totals and metric breakdowns by status and priority.
    Safely handles empty datasets without dividing or crashing.
    """
    total_tickets = len(all_tickets_list)
    
    # Initialize baseline tracking dictionaries with required system states
    status_counts = {"open": 0, "in_progress": 0, "resolved": 0}
    priority_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    # Aggregate counts from our active database entries
    for ticket in all_tickets_list:
        status = ticket.get("status", "open").lower()
        priority = ticket.get("priority", "low").lower()

        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = status_counts.get(status, 0) + 1

        if priority in priority_counts:
            priority_counts[priority] += 1
        else:
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

    # Format and present the metrics cleanly onto the text console interface
    print("\n" + "="*35)
    print("        SYSTEM METRICS REPORT       ")
    print("="*35)
    print(f"Total Tickets Logged: {total_tickets}")
    print("-"*35)
    
    print("Breakdown by Status:")
    for status, count in status_counts.items():
        print(f"  • {status.replace('_', ' ').title()}: {count}")
        
    print("-"*35)
    print("Breakdown by Priority:")
    for priority, count in priority_counts.items():
        print(f"  • {priority.title()}: {count}")
    print("="*35 + "\n")

    return {
        "total": total_tickets,
        "status": status_counts,
        "priority": priority_counts
    }
