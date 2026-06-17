"""Tests for the real event-log loader."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from real_data_loader import load_real_user_features


class RealDataLoaderTest(unittest.TestCase):
    def test_fixture_aggregates_event_logs_to_user_features(self) -> None:
        fixture_path = PROJECT_ROOT / "data" / "fixtures" / "mini_event_log.csv"

        features, metadata = load_real_user_features(
            fixture_path,
            dataset_type="synerise",
        )

        self.assertEqual(metadata["event_count"], 21)
        self.assertEqual(metadata["user_count"], 5)
        self.assertEqual(metadata["event_types"], ["cart", "purchase", "remove_from_cart", "search", "view"])

        row = features.set_index("user_id").loc["U004"]
        self.assertEqual(row["event_count"], 4)
        self.assertEqual(row["cart_count"], 1)
        self.assertEqual(row["purchase_count"], 2)
        self.assertEqual(row["session_count"], 2)
        self.assertEqual(row["price_signal_total"], 570.0)


if __name__ == "__main__":
    unittest.main()
