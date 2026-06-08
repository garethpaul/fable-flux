import unittest

from src.diversity_tracker import DiversityTracker


class DiversityTrackerTests(unittest.TestCase):
    def test_character_selection_includes_unused_candidates(self):
        tracker = DiversityTracker()
        tracker.character_usage["Ada the ant"] = 3

        self.assertEqual(
            "Bea the bee",
            tracker.get_next_character(["Ada the ant", "Bea the bee"]),
        )

    def test_setting_selection_includes_unused_candidates(self):
        tracker = DiversityTracker()
        tracker.setting_usage["library"] = 2

        self.assertEqual("garden", tracker.get_next_setting(["library", "garden"]))

    def test_empty_inputs_raise_clear_errors(self):
        tracker = DiversityTracker()

        with self.assertRaisesRegex(ValueError, "Characters list is empty"):
            tracker.get_next_character([])

        with self.assertRaisesRegex(ValueError, "Settings list is empty"):
            tracker.get_next_setting([])


if __name__ == "__main__":
    unittest.main()
