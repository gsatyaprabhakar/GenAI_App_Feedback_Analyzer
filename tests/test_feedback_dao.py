import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dao import feedback_dao


class FeedbackDaoTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.original_db_file = feedback_dao.DB_FILE
        feedback_dao.DB_FILE = Path(self.temp_dir.name) / "feedback.db"
        feedback_dao.init_db()

    def tearDown(self):
        feedback_dao.DB_FILE = self.original_db_file
        self.temp_dir.cleanup()

    def test_save_and_load_results(self):
        results = [
            {
                "review": "Fast delivery",
                "label": "positive",
                "score": 5,
                "theme": "delivery",
            },
            {
                "review": "Could not analyze",
                "label": "error",
                "score": 0,
                "theme": "error",
            },
        ]

        self.assertEqual(feedback_dao.save_results(results), 1)
        self.assertEqual(
            feedback_dao.load_history(),
            [("Fast delivery", "positive", 5, "delivery")],
        )

    def test_save_empty_results_returns_zero(self):
        self.assertEqual(feedback_dao.save_results([]), 0)


if __name__ == "__main__":
    unittest.main()
