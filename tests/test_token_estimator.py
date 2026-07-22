import json
import unittest

from common.models import PromptMessage
from context.models import ContextWindow
from context.token_estimator import (
    MESSAGE_OVERHEAD_TOKENS,
    REQUEST_OVERHEAD_TOKENS,
    TOOL_SCHEMA_OVERHEAD_TOKENS,
    HeuristicTokenEstimator,
)


class TokenEstimatorTest(unittest.TestCase):
    def setUp(self):
        self.estimator = HeuristicTokenEstimator()

    def test_estimate_text_uses_utf8_bytes(self):
        self.assertEqual(0, self.estimator.estimate_text(None))
        self.assertEqual(0, self.estimator.estimate_text(""))
        self.assertEqual(1, self.estimator.estimate_text("abc"))
        self.assertEqual(2, self.estimator.estimate_text("中文"))
        self.assertEqual(2, self.estimator.estimate_text("😀"))

    def test_estimate_classifies_messages_and_structured_tool_fields(self):
        messages = [
            PromptMessage(role="system", content="abc"),
            PromptMessage(role="user", content="hello"),
            PromptMessage(
                role="assistant",
                tool_calls=[
                    {
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "search", "arguments": "{}"},
                    }
                ],
            ),
            PromptMessage(
                role="tool",
                tool_call_id="call-1",
                content="result",
            ),
        ]
        window = ContextWindow(
            max_context_tokens=100,
            reserved_output_tokens=20,
            safety_tokens=5,
        )

        usage = self.estimator.estimate(messages, [], window)

        self.assertEqual(
            MESSAGE_OVERHEAD_TOKENS + self.estimator.estimate_text("abc"),
            usage.system_tokens,
        )
        self.assertEqual(
            MESSAGE_OVERHEAD_TOKENS + self.estimator.estimate_text("hello"),
            usage.conversation_tokens,
        )
        self.assertGreater(usage.tool_exchange_tokens, 2 * MESSAGE_OVERHEAD_TOKENS)
        self.assertEqual(REQUEST_OVERHEAD_TOKENS, usage.request_overhead_tokens)

    def test_estimate_includes_actual_tool_schema_and_all_totals(self):
        tool_schema = {
            "type": "function",
            "function": {
                "name": "search",
                "parameters": {"type": "object"},
            },
        }
        window = ContextWindow(
            max_context_tokens=10,
            reserved_output_tokens=4,
            safety_tokens=3,
        )

        usage = self.estimator.estimate([], [tool_schema], window)

        serialized = json.dumps(
            tool_schema,
            ensure_ascii=False,
            sort_keys=True,
        )
        expected_tool_tokens = (
            TOOL_SCHEMA_OVERHEAD_TOKENS
            + self.estimator.estimate_text(serialized)
        )
        self.assertEqual(expected_tool_tokens, usage.tool_schema_tokens)
        self.assertEqual(
            expected_tool_tokens + REQUEST_OVERHEAD_TOKENS,
            usage.estimated_input_tokens,
        )
        self.assertEqual(
            10 - 4 - 3 - usage.estimated_input_tokens,
            usage.estimated_remaining_tokens,
        )
        self.assertLess(usage.estimated_remaining_tokens, 0)


if __name__ == "__main__":
    unittest.main()
