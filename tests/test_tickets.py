# tests/test_tickets.py
import unittest
from campusflow.tickets import calculate_priority, validate_status

class TestTicketLogic(unittest.TestCase):
    def test_priority_rules(self):
        # RULE 1: high urgency AND 10 or more affected users -> critical
        self.assertEqual(calculate_priority("high", 15), "critical")
        self.assertEqual(calculate_priority("high", 10), "critical")

        # RULE 2: high urgency OR 10 or more affected users -> high
        self.assertEqual(calculate_priority("high", 5), "high")
        self.assertEqual(calculate_priority("low", 12), "high")

        # RULE 3: medium urgency OR 3 or more affected users -> medium
        self.assertEqual(calculate_priority("medium", 2), "medium")
        self.assertEqual(calculate_priority("low", 4), "medium")

        # RULE 4: remaining valid tickets -> low
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_status_lookup_bounds(self):
        try:
            validate_status("open")
            validate_status("in_progress")
            validate_status("resolved")
        except ValueError:
            self.fail("validate_status raised ValueError unexpectedly on a valid state!")

        with self.assertRaises(ValueError):
            validate_status("pending")

if __name__ == "__main__":
    unittest.main()
