# tests/test_tickets.py
import unittest

from campusflow.tickets import (
    calculate_priority,
    validate_affected_users,
    validate_category,
    validate_status,
    validate_title,
    validate_urgency,
)


class TestPriorityRules(unittest.TestCase):
    def test_rule1_high_urgency_and_many_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")
        self.assertEqual(calculate_priority("high", 10), "critical")  # boundary

    def test_rule2_high_urgency_or_many_users_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")
        self.assertEqual(calculate_priority("low", 10), "high")  # boundary
        self.assertEqual(calculate_priority("medium", 15), "high")

    def test_rule3_medium_urgency_or_some_users_is_medium(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")  # boundary
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_rule4_everything_else_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")
        self.assertEqual(calculate_priority("low", 2), "low")  # boundary


class TestValidators(unittest.TestCase):
    def test_title_is_trimmed_and_blank_titles_rejected(self):
        self.assertEqual(validate_title("  Wi-Fi down  "), "Wi-Fi down")
        for bad in ("", "   ", "\t\n", None, 42):
            with self.assertRaises(ValueError):
                validate_title(bad)

    def test_affected_users_accepts_positive_whole_numbers(self):
        self.assertEqual(validate_affected_users(5), 5)
        self.assertEqual(validate_affected_users("12"), 12)
        self.assertEqual(validate_affected_users(" 7 "), 7)

    def test_affected_users_rejects_zero_negative_text_decimal_bool_none(self):
        for bad in (0, -3, "0", "-3", "ten", "", "5.5", "5.0", 5.5, 5.0, True, False, None):
            with self.assertRaises(ValueError, msg=f"{bad!r} should be rejected"):
                validate_affected_users(bad)

    def test_category_and_urgency_are_normalized(self):
        self.assertEqual(validate_category("  nEtWoRk "), "Network")
        self.assertEqual(validate_urgency(" HIGH "), "high")
        with self.assertRaises(ValueError):
            validate_category("Plumbing")
        with self.assertRaises(ValueError):
            validate_urgency("urgent")

    def test_status_lookup_bounds(self):
        for good in ("open", "in_progress", "resolved"):
            self.assertEqual(validate_status(good), good)
        with self.assertRaises(ValueError):
            validate_status("pending")


if __name__ == "__main__":
    unittest.main()