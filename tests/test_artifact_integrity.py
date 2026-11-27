import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from src.evaluation.package_evaluation import verify


class ArtifactIntegrityTests(unittest.TestCase):
    def bundle(self, folder, payload, expected_payload):
        path = Path(folder) / 'test.zip'
        manifest = {'files': {'input.json': {
            'bytes': len(expected_payload),
            'sha256': hashlib.sha256(expected_payload).hexdigest(),
        }}}
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('input.json', payload)
            z.writestr('MANIFEST.json', json.dumps(manifest))
        return path

    def test_exact_saved_bytes_verify(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIn('files', verify(self.bundle(folder, b'{}', b'{}')))

    def test_changed_saved_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                verify(self.bundle(folder, b'[]', b'{}'))


if __name__ == '__main__':
    unittest.main()
