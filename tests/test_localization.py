import unittest
from src.evaluation.evaluate_localization import score


def worksheet(truth, predictions, links, status='matched'):
    return [{'example_id': 'x', 'matching_reviewed': True,
             'predicted_parts': [{'prediction_number': i, 'label': p} for i, p in enumerate(predictions, 1)],
             'reference_parts': [{'label': truth, 'match_status': status,
                                  'matched_prediction_numbers': links}]}]


class LocalizationTests(unittest.TestCase):
    def test_wrong_error_subtype_is_detection_but_not_exact(self):
        result = score(worksheet('unsupported', ['contradicted'], [1]))
        self.assertEqual(result['counts']['tp'], 1)
        self.assertEqual(result['exact_reference_coverage'], 0)

    def test_fallback_error_is_false_negative(self):
        result = score(worksheet('unsupported', [], [], 'no_component_output'))
        self.assertEqual(result['counts']['fn'], 1)
        self.assertEqual(result['reference_aligned_error_detection']['recall'], 0)
        self.assertIsNone(result['reference_aligned_error_detection']['precision'])

    def test_linked_mixed_labels_do_not_duplicate_reference(self):
        result = score(worksheet('unsupported', ['unsupported', 'supported'], [1, 2]))
        self.assertEqual(result['counts']['reference_details'], 1)
        self.assertEqual(result['counts']['tp'], 1)
        self.assertEqual(result['counts']['exact_correct'], 0)

    def test_false_alarm_and_unmatched_prediction_are_separate(self):
        result = score(worksheet('supported', ['unsupported', 'contradicted'], [1]))
        self.assertEqual(result['counts']['fp'], 1)
        self.assertEqual(result['counts']['unmatched_error_predictions'], 1)

    def test_invalid_linked_label_remains_in_denominator(self):
        result = score(worksheet('unsupported', [None], [1]))
        self.assertEqual(result['counts']['fn'], 1)
        self.assertEqual(result['counts']['invalid_linked_judgment'], 1)
        self.assertEqual(result['exact_reference_coverage'], 0)

    def test_unknown_link_rejected(self):
        with self.assertRaises(ValueError):
            score(worksheet('supported', ['supported'], [2]))


if __name__ == '__main__':
    unittest.main()
