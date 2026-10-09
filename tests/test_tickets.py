import unittest
from campusflow.tickets import Ticket, validate_ticket

class TestTicketValidation(unittest.TestCase):

    def test_valid_ticket_passes(self):
        """Valid tickets should return True smoothly."""
        ticket = Ticket(
            id="TCK-101",
            title="Wi-Fi Router failure in Dorm B",
            category="IT",
            urgency="High",
            affected_users=25,
            priority="High",
            status="Open",
            assigned_to="Helpdesk"
        )
        self.assertTrue(validate_ticket(ticket))

    def test_empty_title_fails(self):
        """Tickets with a blank title should raise a ValueError."""
        ticket = Ticket("TCK-102", "", "IT", "Low", 5, "Low", "Open", "Staff")
        with self.assertRaises(ValueError) as context:
            validate_ticket(ticket)
        self.assertEqual(str(context.exception), "Validation Failed: Title cannot be empty.")

    def test_whitespace_title_fails(self):
        """Tickets with only spaces in the title should raise a ValueError."""
        ticket = Ticket("TCK-103", "   ", "IT", "Low", 5, "Low", "Open", "Staff")
        with self.assertRaises(ValueError) as context:
            validate_ticket(ticket)
        self.assertEqual(str(context.exception), "Validation Failed: Title cannot be just blank spaces.")

    def test_empty_status_fails(self):
        """Tickets missing a status should raise a ValueError."""
        ticket = Ticket("TCK-104", "Fix leak", "Facilities", "Medium", 2, "Medium", "", "Janitor")
        with self.assertRaises(ValueError) as context:
            validate_ticket(ticket)
        self.assertEqual(str(context.exception), "Validation Failed: Status cannot be empty.")

    def test_affected_users_zero_fails(self):
        """Tickets impacting exactly 0 users must be rejected."""
        ticket = Ticket("TCK-105", "Printer jam", "IT", "Low", 0, "Low", "Open", "Helpdesk")
        with self.assertRaises(ValueError) as context:
            validate_ticket(ticket)
        self.assertEqual(str(context.exception), "Validation Failed: affected_users cannot be 0.")

    def test_affected_users_negative_fails(self):
        """Tickets impacting negative users must be rejected."""
        ticket = Ticket("TCK-106", "Broken window", "Facilities", "High", -3, "High", "Open", "Admin")
        with self.assertRaises(ValueError) as context:
            validate_ticket(ticket)
        self.assertEqual(str(context.exception), "Validation Failed: affected_users cannot be negative.")

if __name__ == "__main__":
    unittest.main()
