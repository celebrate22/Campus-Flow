import json

class TicketStorage:
    def __init__(self, filename="tickets.json"):
        """Initializes the storage manager with a target JSON file."""
        self.filename = filename
        self._current_id_counter = 0

    def find_highest_existing_id(self, loaded_data):
        """
        Requirement: 'IDs must remain unique after reload'
        Scans loaded records to see what the last ID number was so it can safely 
        prevent duplicate ID clashes after a restart.
        """
        highest = 0
        for ticket_id in loaded_data.keys():
            if ticket_id.startswith("T") and ticket_id[1:].isdigit():
                num = int(ticket_id[1:])
                if num > highest:
                    highest = num
        return highest

    def generate_next_sequential_id(self):
        """
        Requirement: 'Ticket IDs are unique and automatically generated (T001, T002, ...)'
        Increments your persistent counter and outputs formatted IDs.
        """
        self._current_id_counter += 1
        return f"T{self._current_id_counter:03d}"

    def load_tickets_from_json(self):
        """
        Requirement: 'reload on startup. Missing file should allow a fresh start; 
        malformed JSON should produce a clear error rather than silently erase data.'
        """
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if not isinstance(data, dict):
                    raise ValueError("Stored data must be a JSON object mapping IDs to ticket data.")
                
                # Align the ID counter with existing records so IDs remain unique after reload
                self._current_id_counter = self.find_highest_existing_id(data)
                return data

        except FileNotFoundError:
            # Missing file: Allow a fresh start smoothly without crashing
            self._current_id_counter = 0
            return {}

        except json.JSONDecodeError as e:
            # Malformed JSON: Produce a clear error rather than silently erasing data
            raise ValueError(
                f"Data Persistence Error: The file '{self.filename}' is corrupted or contains malformed JSON.\n"
                f"Details: {str(e)}\n"
                f"Please repair the file manually or move it to start fresh."
            ) from e

    def save_tickets_to_json(self, all_tickets):
        """
        Requirement: 'Save to JSON'
        Converts active tickets to JSON text and writes them safely to your disk drive.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(all_tickets, f, indent=4)
        except IOError as e:
            raise IOError(f"Failed to write ticket data to storage file '{self.filename}': {str(e)}")
