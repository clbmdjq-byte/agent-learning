import unittest
from unittest.mock import patch

from config.config import LlmClientConfig


class LlmClientConfigTest(unittest.TestCase):
    def test_from_env_reads_context_window_configuration(self):
        with patch.dict(
            "os.environ",
            {
                "BASE_URL": "https://example.com",
                "MODEL": "test-model",
                "API_KEY": "test-key",
                "MAX_TOKENS": "256",
                "MAX_CONTEXT_TOKENS": "4096",
                "CONTEXT_SAFETY_TOKENS": "64",
            },
            clear=True,
        ):
            config = LlmClientConfig.from_env()

        self.assertEqual(256, config.max_tokens)
        self.assertEqual(4096, config.max_context_tokens)
        self.assertEqual(64, config.context_safety_tokens)


if __name__ == "__main__":
    unittest.main()
