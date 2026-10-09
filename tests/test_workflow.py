# tests/test_workflow.py
import unittest
import os
from campusflow.storage import TicketStorage
from campusflow.workflow import WorkflowEngine

class TestWorkflowEngine(unittest.TestCase):
    """Tests core business behavior, work queues, and validation state limits within workflow.py"""

    def setUp(self):
        self.test_filename = "test_workflow_temp.json"
        self.storage = TicketStorage(self.test_filename)
        self.engine = WorkflowEngine(self.storage)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_create_ticket_with_normalization_and_validation(self):
        """Requirement F1 & 1.2: Rejects bad fields and normalizes valid string case variants."""
        with self.assertRaises(ValueError):
            self.engine.create_and_store_ticket({
                "title": "   ", "category": "Network", "urgency": "low", "affected_users": 5
            })

        with self.assertRaises(ValueError):
            self.engine.create_and_store_ticket({
                "title": "Fix IT", "category": "Network", "urgency": "low", "affected_users": "ten"
            })

        raw_input = {
            "title": "Database lag",
            "category": "software",
            "urgency": "HIGH",
            "affected_users": "12"
        }
        ticket_id = self.engine.create_and_store_ticket(raw_input)
        created_ticket = self.engine.get_single_ticket_by_id(ticket_id)

        self.assertEqual(created_ticket["category"], "Software")
        self.assertEqual(created_ticket["urgency"], "high")
        self.assertEqual(created_ticket["affected_users"], 12)
        self.assertEqual(created_ticket["priority"], "critical")

    def test_workflow_state_restrictions(self):
        """Requirement F4: Blocks unassigned tickets from in_progress and locks down resolved states."""
        ticket_id = self.engine.create_and_store_ticket({
            "title": "Server Leak", "category": "Hardware", "urgency": "low", "affected_users": 1
        })

        with self.assertRaises(ValueError):
            self.engine.transition_ticket_status(ticket_id, "in_progress")

        self.engine.assign_ticket_to_staff(ticket_id, "Alice")
        self.engine.transition_ticket_status(ticket_id, "in_progress")
        self.engine.transition_ticket_status(ticket_id, "resolved")

        with self.assertRaises(ValueError):
            self.engine.assign_ticket_to_staff(ticket_id, "Bob")

        self.engine.transition_ticket_status(ticket_id, "open")
        self.assertEqual(self.engine.get_single_ticket_by_id(ticket_id)["status"], "open")

    def test_work_queue_sorting_and_tie_breaking(self):
        """Requirement F5: Active items sort by priority tier, then tie-break by earlier ticket numeric ID."""
        self.engine.create_and_store_ticket({
            "title": "Low Priority Item", "category": "Other", "urgency": "low", "affected_users": 1
        })
        self.engine.create_and_store_ticket({
            "title": "Critical Priority Item A", "category": "Network", "urgency": "high", "affected_users": 20
        })
        self.engine.create_and_store_ticket({
            "title": "Critical Priority Item B", "category": "Network", "urgency": "high", "affected_users": 50
        })

        queue = self.engine.get_sorted_work_queue()
        
        self.assertEqual(len(queue), 3)
        self.assertEqual(queue[0]["id"], "T002")
        self.assertEqual(queue[1]["id"], "T003")
        self.assertEqual(queue[2]["id"], "T001")

if __name__ == "__main__":
    unittest.main()
