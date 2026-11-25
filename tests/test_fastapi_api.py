import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api.fastapi_api import app


class FastApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_reports_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")

    def test_analyze_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post("/analyze", json={"text": "Great food"})

        self.assertEqual(response.status_code, 503)

    def test_review_rejects_blank_text(self):
        response = self.client.post("/analyze", json={"text": "   "})

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
