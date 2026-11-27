"""Exercise user-facing input safety, method routing, and failure persistence."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.evaluation.check_claim import main


class CheckClaimTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source.txt'
        self.source.write_text('The film was released in 2016.', encoding='utf-8')
        self.args = ['--claim', 'The film was released in 2016.', '--source', str(self.source)]

    def invoke(self, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(args)

    @patch('src.evaluation.run_prompted.predict')
    def test_prepare_makes_no_inference_call(self, predict):
        self.assertEqual(self.invoke(self.args + ['--prepare-only']), 0)
        predict.assert_not_called()

    @patch('src.evaluation.run_prompted.predict')
    def test_existing_output_preserved_without_inference(self, predict):
        output = Path(self.temp.name) / 'result.json'
        output.write_text('original')
        with self.assertRaises(SystemExit) as result:
            self.invoke(self.args + ['--output', str(output)])
        self.assertEqual(result.exception.code, 2)
        self.assertEqual(output.read_text(), 'original')
        predict.assert_not_called()

    @patch('src.evaluation.run_prompted.predict')
    def test_default_routes_to_components_and_persists_provenance(self, predict):
        predict.return_value = ('complete_support', {'components': []})
        output = Path(self.temp.name) / 'result.json'
        self.assertEqual(self.invoke(self.args + ['--output', str(output)]), 0)
        predict.assert_called_once_with('components', 'ollama:qwen2.5:7b', self.args[1], self.source.read_text())
        report = json.loads(output.read_text())
        self.assertEqual(report['method'], 'components')
        self.assertEqual(len(report['source_sha256']), 64)

    @patch('src.evaluation.verified_pipeline.predict_verified')
    def test_verified_route_is_explicit(self, predict):
        predict.return_value = ('no_support', {})
        self.assertEqual(self.invoke(self.args + ['--method', 'components_verified']), 0)
        predict.assert_called_once()

    @patch('src.evaluation.run_prompted.predict')
    def test_failure_saved_and_nonzero_exit(self, predict):
        predict.side_effect = ValueError('Invalid number of components')
        output = Path(self.temp.name) / 'failed.json'
        self.assertEqual(self.invoke(self.args + ['--output', str(output)]), 1)
        report = json.loads(output.read_text())
        self.assertIsNone(report['prediction'])
        self.assertEqual(report['error'], 'Invalid number of components')

    def test_bad_encoding_rejected_as_input_error(self):
        self.source.write_bytes(b'\xff\xfe')
        with self.assertRaises(SystemExit) as result:
            self.invoke(self.args + ['--prepare-only'])
        self.assertEqual(result.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
