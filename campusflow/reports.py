# campusflow/reports.py
"""F6 - totals and breakdowns by status and priority."""

STATUS_ORDER = ("open", "in_progress", "resolved")
PRIORITY_ORDER = ("critical", "high", "medium", "low")


def build_summary(all_tickets_list):
    """Pure calculation: count tickets. Safe for an empty list."""
    status_counts = {name: 0 for name in STATUS_ORDER}
    priority_counts = {name: 0 for name in PRIORITY_ORDER}

    for ticket in all_tickets_list:
        status = str(ticket.get("status") or "open").lower()
        priority = str(ticket.get("priority") or "low").lower()
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    return {
        "total": len(all_tickets_list),
        "status": status_counts,
        "priority": priority_counts,
    }


def generate_system_summary_report(all_tickets_list, display=True):
    """Build the summary, optionally print it, and return the numbers."""
    summary = build_summary(all_tickets_list)

    if display:
        print("\n" + "=" * 35)
        print("        SYSTEM METRICS REPORT")
        print("=" * 35)
        print(f"Total Tickets Logged: {summary['total']}")
        print("-" * 35)
        print("Breakdown by Status:")
        for status, count in summary["status"].items():
            print(f"  - {status.replace('_', ' ').title()}: {count}")
        print("-" * 35)
        print("Breakdown by Priority:")
        for priority, count in summary["priority"].items():
            print(f"  - {priority.title()}: {count}")
        print("=" * 35 + "\n")

    return summary