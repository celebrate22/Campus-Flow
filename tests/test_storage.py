# tests/test_storage.py
import json
import os
import tempfile
import unittest

from campusflow.storage import TicketStorage


class TestStorage(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.path = os.path.join(self.dir, "tickets.json")
        self.storage = TicketStorage(self.path)

    def test_missing_file_allows_fresh_start(self):
        self.assertEqual(self.storage.load_tickets_from_json(), {})
        self.assertEqual(self.storage.generate_next_sequential_id(), "T001")

    def test_malformed_json_produces_clear_error_and_keeps_file(self):
        broken = "{ broken json string: ,,, ]"
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(broken)
        with self.assertRaises(ValueError) as ctx:
            self.storage.load_tickets_from_json()
        self.assertIn("Data Persistence Error", str(ctx.exception))
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), broken)  # nothing was erased

    def test_wrong_json_shape_is_rejected(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)
        with self.assertRaises(ValueError):
            self.storage.load_tickets_from_json()

    def test_ids_remain_unique_after_reload(self):
        stub = {"T001": {"id": "T001"}, "T004": {"id": "T004"}}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(stub, f)
        self.storage.load_tickets_from_json()
        self.assertEqual(self.storage.generate_next_sequential_id(), "T005")

    def test_save_and_reload_round_trip(self):
        data = {"T001": {"id": "T001", "title": "Wi-Fi", "assigned_to": None}}
        self.storage.save_tickets_to_json(data)
        reloaded = TicketStorage(self.path).load_tickets_from_json()
        self.assertEqual(reloaded, data)

    def test_save_creates_missing_folder_and_leaves_no_temp_files(self):
        nested = os.path.join(self.dir, "data", "tickets.json")
        TicketStorage(nested).save_tickets_to_json({"T001": {"id": "T001"}})
        self.assertTrue(os.path.exists(nested))
        self.assertEqual(os.listdir(os.path.dirname(nested)), ["tickets.json"])

    def test_release_id_gives_back_last_id(self):
        first = self.storage.generate_next_sequential_id()
        self.storage.release_id(first)
        self.assertEqual(self.storage.generate_next_sequential_id(), "T001")


if __name__ == "__main__":
    unittest.main()