# tests/test_storage.py
import json
import unittest
import os
from campusflow.storage import TicketStorage

class TestStorageManager(unittest.TestCase):
    """Tests persistence constraints, corruption trapping, and fresh starts inside storage.py"""
    
    def setUp(self):
        self.test_filename = "test_storage_temp.json"
        self.storage = TicketStorage(self.test_filename)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_missing_file_allows_fresh_start(self):
        """Requirement F7: Missing file shouldn't crash; should yield empty database."""
        data = self.storage.load_tickets_from_json()
        self.assertEqual(data, {})
        self.assertEqual(self.storage.generate_next_sequential_id(), "T001")

    def test_malformed_json_produces_clear_error(self):
        """Requirement F7: Malformed syntax throws meaningful Data Persistence Error."""
        with open(self.test_filename, "w", encoding="utf-8") as f:
            f.write("{ broken json string: ,,, ]")

        with self.assertRaises(ValueError) as ctx:
            self.storage.load_tickets_from_json()
        
        self.assertIn("Data Persistence Error", str(ctx.exception))

    def test_ids_remain_unique_after_reload(self):
        """Requirement F7: Counter must sync to highest loaded index to prevent overlaps."""
        stub_data = {
            "T001": {"id": "T001", "title": "First Ticket"},
            "T004": {"id": "T004", "title": "Highest Ticket"}
        }
        with open(self.test_filename, "w", encoding="utf-8") as f:
            json.dump(stub_data, f)

        self.storage.load_tickets_from_json()
        self.assertEqual(self.storage.generate_next_sequential_id(), "T005")

if __name__ == "__main__":
    unittest.main()
