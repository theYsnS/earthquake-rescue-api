"""Tests for earthquake rescue API."""

import os
import unittest
from src.models.database import Database, haversine


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database("test_rescue.db")

    def tearDown(self):
        if os.path.exists("test_rescue.db"):
            os.remove("test_rescue.db")

    def test_create_report(self):
        report = self.db.create_report({
            "latitude": 39.92, "longitude": 32.85,
            "severity": "high", "description": "Building collapsed"
        })
        self.assertIn("id", report)

    def test_haversine(self):
        dist = haversine(39.92, 32.85, 39.93, 32.86)
        self.assertGreater(dist, 0)
        self.assertLess(dist, 5)

    def test_stats(self):
        stats = self.db.get_stats()
        self.assertIn("total_reports", stats)


if __name__ == "__main__":
    unittest.main()
