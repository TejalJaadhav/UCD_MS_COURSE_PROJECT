"""Check evaluation failures, label integrity, and class-balanced metrics."""

import unittest
from unittest.mock import patch

from src.evaluation.overall import LABELS, evaluate, metrics


class OverallTests(unittest.TestCase):
    def test_perfect_predictions(self):
        result = metrics(list(LABELS), list(LABELS))
        self.assertEqual(result["accuracy"], 1)
        self.assertEqual(result["macro_f1"], 1)

    def test_failures_are_not_dropped(self):
        result = metrics(list(LABELS), [LABELS[0], None, None])
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["failed"], 2)
        self.assertAlmostEqual(result["accuracy"], 1 / 3)
        self.assertEqual(result["per_class"][LABELS[1]]["recall"], 0)

    def test_majority_macro_f1_includes_missing_predictions(self):
        result = metrics([LABELS[0]] * 3 + [LABELS[1]], [LABELS[0]] * 4)
        self.assertAlmostEqual(result["macro_f1"], (6 / 7) / 3)

    def test_rejects_nli_labels(self):
        with self.assertRaises(ValueError):
            metrics([LABELS[0]], ["entailment"])

    @patch("src.evaluation.overall.load_split")
    def test_rejects_changed_gold_and_missing_rows(self, load):
        load.return_value = ([{"example_id": "dev_00001", "gold_label": LABELS[0]}], "hash")
        report = dict(split="dev", dataset_version="raw", dataset_sha256="hash",
                      example_ids=["dev_00001"], predictions=[])
        with self.assertRaises(ValueError):
            evaluate(report)
        report["predictions"] = [{"example_id": "dev_00001", "gold_label": LABELS[1],
                                  "prediction": LABELS[1]}]
        with self.assertRaises(ValueError):
            evaluate(report)


if __name__ == "__main__":
    unittest.main()
