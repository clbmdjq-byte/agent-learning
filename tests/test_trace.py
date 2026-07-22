import unittest

from context.models import ContextUsage
from trace.trace import AgentTrace


def build_usage() -> ContextUsage:
    return ContextUsage(
        system_tokens=10,
        conversation_tokens=20,
        tool_exchange_tokens=30,
        tool_schema_tokens=40,
        request_overhead_tokens=3,
        estimated_input_tokens=103,
        max_context_tokens=1000,
        reserved_output_tokens=100,
        safety_tokens=20,
        estimated_remaining_tokens=777,
    )


class AgentTraceTest(unittest.TestCase):
    def test_format_displays_context_usage(self):
        trace = AgentTrace("hello")
        trace.add_context_usage(build_usage())

        rendered = trace.format()

        self.assertIn("[Context Usage]", rendered)
        self.assertIn('"estimated_input_tokens": 103', rendered)
        self.assertIn('"estimated_remaining_tokens": 777', rendered)

    def test_format_displays_none_without_context_usage(self):
        trace = AgentTrace("hello")

        rendered = trace.format()

        self.assertIn("[Context Usage]\nnone", rendered)


if __name__ == "__main__":
    unittest.main()
