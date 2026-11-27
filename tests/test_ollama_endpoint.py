"""Verify container endpoint routing without changing inference payloads."""
import json
import os
import unittest
from unittest.mock import MagicMock, patch
from src.evaluation.run_prompted import ask_local

class OllamaEndpointTests(unittest.TestCase):
    def check_endpoint(self, environment, expected):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "message": {"content": json.dumps({"label": "supported"})}
        }).encode()
        with patch.dict(os.environ, environment, clear=True), patch(
            "src.evaluation.run_prompted.urlopen", return_value=response
        ) as call:
            ask_local("qwen2.5:7b", "instruction", {"claim": "example"},
                      {"label": {"type": "string", "enum": ["supported"]}})
        request = call.call_args.args[0]
        self.assertEqual(request.full_url, expected)
        payload = json.loads(request.data)
        self.assertEqual(payload["options"], {"temperature": 0, "seed": 42, "num_ctx": 4096})

    def test_native_default(self):
        self.check_endpoint({}, "http://127.0.0.1:11434/api/chat")

    def test_container_override_trailing_slash(self):
        self.check_endpoint({"OLLAMA_BASE_URL": "http://host.docker.internal:11434/"},
                            "http://host.docker.internal:11434/api/chat")
