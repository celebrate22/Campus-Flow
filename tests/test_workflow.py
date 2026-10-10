# tests/test_workflow.py
import os
import tempfile
import unittest
from unittest import mock

from campusflow.storage import TicketStorage
from campusflow.workflow import WorkflowEngine


def ticket_input(**overrides):
    base = {"title": "Printer jam", "category": "Hardware", "urgency": "low", "affected_users": 1}
    base.update(overrides)
    return base


class WorkflowTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = os.path.join(tmp.name, "tickets.json")
        self.engine = self.new_engine()

    def new_engine(self):
        return WorkflowEngine(TicketStorage(self.path))


class TestCreate(WorkflowTestCase):
    def test_valid_ticket_is_normalized_and_prioritized(self):
        tid = self.engine.create_and_store_ticket(
            ticket_input(title="  Database lag ", category="software", urgency="HIGH", affected_users="12")
        )
        t = self.engine.get_single_ticket_by_id(tid)
        self.assertEqual(tid, "T001")
        self.assertEqual(t["title"], "Database lag")
        self.assertEqual(t["category"], "Software")
        self.assertEqual(t["urgency"], "high")
        self.assertEqual(t["affected_users"], 12)
        self.assertEqual(t["priority"], "critical")
        self.assertEqual(t["status"], "open")
        self.assertIsNone(t["assigned_to"])

    def test_invalid_inputs_are_rejected_without_storing_anything(self):
        bad_inputs = [
            ticket_input(title="   "),
            ticket_input(category="Plumbing"),
            ticket_input(urgency="urgent"),
            ticket_input(affected_users=0),
            ticket_input(affected_users=-2),
            ticket_input(affected_users="ten"),
            ticket_input(affected_users=2.5),
        ]
        for bad in bad_inputs:
            with self.assertRaises(ValueError, msg=str(bad)):
                self.engine.create_and_store_ticket(bad)
        self.assertEqual(self.engine.get_all_tickets_list(), [])
        # A rejected ticket must not use up an ID.
        self.assertEqual(self.engine.create_and_store_ticket(ticket_input()), "T001")

    def test_failed_save_rolls_back_the_new_ticket(self):
        with mock.patch.object(self.engine.storage, "save_tickets_to_json", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.engine.create_and_store_ticket(ticket_input())
        self.assertEqual(self.engine.get_all_tickets_list(), [])
        self.assertEqual(self.engine.create_and_store_ticket(ticket_input()), "T001")


class TestPersistence(WorkflowTestCase):
    def test_tickets_survive_restart_and_new_ids_do_not_clash(self):
        first = self.engine.create_and_store_ticket(ticket_input(title="One"))
        second = self.engine.create_and_store_ticket(ticket_input(title="Two"))

        restarted = self.new_engine()
        self.assertEqual(restarted.get_single_ticket_by_id(first)["title"], "One")
        self.assertEqual(restarted.get_single_ticket_by_id(second)["title"], "Two")

        third = restarted.create_and_store_ticket(ticket_input(title="Three"))
        self.assertEqual(third, "T003")
        self.assertEqual(len(restarted.get_all_tickets_list()), 3)

    def test_status_and_assignment_survive_restart(self):
        tid = self.engine.create_and_store_ticket(ticket_input())
        self.engine.assign_ticket_to_staff(tid, "Alice")
        self.engine.transition_ticket_status(tid, "in_progress")
        t = self.new_engine().get_single_ticket_by_id(tid)
        self.assertEqual(t["assigned_to"], "Alice")
        self.assertEqual(t["status"], "in_progress")


class TestAssignAndWorkflow(WorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.tid = self.engine.create_and_store_ticket(ticket_input())

    def status(self):
        return self.engine.get_single_ticket_by_id(self.tid)["status"]

    def test_unknown_ticket_id_is_rejected(self):
        with self.assertRaises(KeyError):
            self.engine.get_single_ticket_by_id("T999")
        with self.assertRaises(KeyError):
            self.engine.assign_ticket_to_staff("T999", "Alice")
        with self.assertRaises(KeyError):
            self.engine.transition_ticket_status("T999", "in_progress")

    def test_blank_staff_name_is_rejected(self):
        for bad in ("", "   ", None):
            with self.assertRaises(ValueError):
                self.engine.assign_ticket_to_staff(self.tid, bad)
        self.assertIsNone(self.engine.get_single_ticket_by_id(self.tid)["assigned_to"])

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        with self.assertRaises(ValueError):
            self.engine.transition_ticket_status(self.tid, "in_progress")
        self.assertEqual(self.status(), "open")

    def test_full_lifecycle_open_to_in_progress_to_resolved(self):
        self.engine.assign_ticket_to_staff(self.tid, "  Alice ")
        self.assertEqual(self.engine.get_single_ticket_by_id(self.tid)["assigned_to"], "Alice")
        self.engine.transition_ticket_status(self.tid, "in_progress")
        self.assertEqual(self.status(), "in_progress")
        self.engine.transition_ticket_status(self.tid, " RESOLVED ")
        self.assertEqual(self.status(), "resolved")

    def test_invalid_transitions_are_rejected_and_change_nothing(self):
        self.engine.assign_ticket_to_staff(self.tid, "Alice")
        for bad in ("resolved", "open", "pending", "", "   "):
            with self.assertRaises(ValueError, msg=bad):
                self.engine.transition_ticket_status(self.tid, bad)
        self.assertEqual(self.status(), "open")

    def test_resolved_ticket_is_locked_until_reopened(self):
        self.engine.assign_ticket_to_staff(self.tid, "Alice")
        self.engine.transition_ticket_status(self.tid, "in_progress")
        self.engine.transition_ticket_status(self.tid, "resolved")

        with self.assertRaises(ValueError):
            self.engine.assign_ticket_to_staff(self.tid, "Bob")
        with self.assertRaises(ValueError):
            self.engine.transition_ticket_status(self.tid, "in_progress")

        self.engine.transition_ticket_status(self.tid, "open")  # explicit reopen
        self.assertEqual(self.status(), "open")
        self.engine.assign_ticket_to_staff(self.tid, "Bob")  # allowed again

    def test_failed_save_rolls_back_assignment_and_status(self):
        self.engine.assign_ticket_to_staff(self.tid, "Alice")
        with mock.patch.object(self.engine.storage, "save_tickets_to_json", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.engine.transition_ticket_status(self.tid, "in_progress")
            with self.assertRaises(OSError):
                self.engine.assign_ticket_to_staff(self.tid, "Bob")
        t = self.engine.get_single_ticket_by_id(self.tid)
        self.assertEqual(t["status"], "open")
        self.assertEqual(t["assigned_to"], "Alice")

    def test_returned_tickets_are_copies_so_rules_cannot_be_bypassed(self):
        self.engine.get_single_ticket_by_id(self.tid)["status"] = "resolved"
        self.assertEqual(self.status(), "open")


class TestWorkQueue(WorkflowTestCase):
    def test_sorted_by_priority_then_earlier_id(self):
        self.engine.create_and_store_ticket(ticket_input(title="Low", urgency="low", affected_users=1))        # T001 low
        self.engine.create_and_store_ticket(ticket_input(title="Crit A", urgency="high", affected_users=20))   # T002 critical
        self.engine.create_and_store_ticket(ticket_input(title="Crit B", urgency="high", affected_users=50))   # T003 critical
        self.engine.create_and_store_ticket(ticket_input(title="Med", urgency="medium", affected_users=1))     # T004 medium
        self.engine.create_and_store_ticket(ticket_input(title="High", urgency="high", affected_users=2))      # T005 high
        queue_ids = [t["id"] for t in self.engine.get_sorted_work_queue()]
        self.assertEqual(queue_ids, ["T002", "T003", "T005", "T004", "T001"])

    def test_numeric_id_tie_break_beyond_nine(self):
        for _ in range(11):
            self.engine.create_and_store_ticket(ticket_input())
        queue_ids = [t["id"] for t in self.engine.get_sorted_work_queue()]
        self.assertEqual(queue_ids[:3], ["T001", "T002", "T003"])
        self.assertEqual(queue_ids[-1], "T011")  # T11 after T9, not before

    def test_queue_excludes_resolved_and_in_progress_tickets(self):
        a = self.engine.create_and_store_ticket(ticket_input(title="A"))
        b = self.engine.create_and_store_ticket(ticket_input(title="B"))
        self.engine.create_and_store_ticket(ticket_input(title="C"))
        for tid in (a, b):
            self.engine.assign_ticket_to_staff(tid, "Alice")
            self.engine.transition_ticket_status(tid, "in_progress")
        self.engine.transition_ticket_status(b, "resolved")
        self.assertEqual([t["id"] for t in self.engine.get_sorted_work_queue()], ["T003"])

    def test_empty_queue(self):
        self.assertEqual(self.engine.get_sorted_work_queue(), [])


if __name__ == "__main__":
    unittest.main()