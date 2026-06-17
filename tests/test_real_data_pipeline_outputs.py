"""Tests for real-data pipeline output path helpers."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from run_real_data_pipeline import build_output_paths, save_review_sample


class RealDataPipelineOutputTest(unittest.TestCase):
    def test_output_tag_adds_suffix_before_extension(self) -> None:
        paths = build_output_paths("300k")

        self.assertEqual(paths["summary"].name, "real_data_summary_300k.md")
        self.assertEqual(paths["figure"].name, "real_data_pca_anomalies_300k.png")
        self.assertEqual(paths["review_sample"].name, "real_anomaly_review_sample_300k.csv")

    def test_review_sample_uses_anonymized_review_ids(self) -> None:
        data = pd.DataFrame(
            {
                "user_id": ["raw_user_a", "raw_user_b"],
                "is_anomaly": [1, 1],
                "anomaly_score": [0.9, 0.8],
                "anomaly_type": ["high_activity_anomaly", "low_conversion_anomaly"],
                "anomaly_evidence": ["high event_count", "low conversion_rate"],
                "suggested_action": ["Review event history.", "Inspect conversion funnel."],
                "event_count": [100, 50],
                "view_count": [80, 45],
                "cart_count": [10, 2],
                "remove_from_cart_count": [5, 0],
                "purchase_count": [3, 0],
                "search_count": [2, 1],
                "unique_items": [20, 10],
                "active_days": [5, 2],
                "price_signal_total": [120.0, 0.0],
                "conversion_rate": [0.0375, 0.0],
                "cart_to_purchase_rate": [0.3, 0.0],
                "cluster": [1, 2],
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            sample_path = Path(tmpdir) / "sample.csv"
            save_review_sample(data, sample_path, sample_size=2)
            sample = pd.read_csv(sample_path)

        self.assertIn("review_user_id", sample.columns)
        self.assertNotIn("user_id", sample.columns)
        self.assertEqual(sample.loc[0, "review_user_id"], "review_user_001")


if __name__ == "__main__":
    unittest.main()
