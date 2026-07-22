import unittest

from pydantic import ValidationError

from common.models import PromptMessage
from context.models import ContextDraft, ToolExchange
from memory.models import ShortTermMemory


def build_memory() -> ShortTermMemory:
    return ShortTermMemory(
        session_id="session-1",
        created_at=1,
        updated_at=1,
    )


def build_assistant_tool_message() -> PromptMessage:
    return PromptMessage(
        role="assistant",
        tool_calls=[
            {
                "id": "call-1",
                "type": "function",
                "function": {"name": "tool-1", "arguments": "{}"},
            },
            {
                "id": "call-2",
                "type": "function",
                "function": {"name": "tool-2", "arguments": "{}"},
            },
        ],
    )


class ContextModelsTest(unittest.TestCase):
    def test_context_draft_rejects_blank_user_input(self):
        with self.assertRaisesRegex(ValidationError, "user_input is required"):
            ContextDraft(user_input="  ", short_memory=build_memory())

    def test_tool_exchange_accepts_matching_tool_results(self):
        exchange = ToolExchange(
            assistant_message=build_assistant_tool_message(),
            tool_messages=[
                PromptMessage(
                    role="tool",
                    tool_call_id="call-1",
                    content='{"result": 1}',
                ),
                PromptMessage(
                    role="tool",
                    tool_call_id="call-2",
                    content='{"result": 2}',
                ),
            ],
        )

        self.assertEqual(2, len(exchange.tool_messages))

    def test_tool_exchange_rejects_non_assistant_call_message(self):
        with self.assertRaisesRegex(
            ValidationError,
            "assistant_message must use assistant role",
        ):
            ToolExchange(
                assistant_message=PromptMessage(role="user", content="hello"),
                tool_messages=[],
            )

    def test_tool_exchange_rejects_missing_tool_result(self):
        with self.assertRaisesRegex(
            ValidationError,
            "tool result ids must match tool call ids",
        ):
            ToolExchange(
                assistant_message=build_assistant_tool_message(),
                tool_messages=[
                    PromptMessage(
                        role="tool",
                        tool_call_id="call-1",
                        content='{"result": 1}',
                    )
                ],
            )

    def test_tool_exchange_rejects_non_tool_result_message(self):
        with self.assertRaisesRegex(
            ValidationError,
            "tool_messages must use tool role",
        ):
            ToolExchange(
                assistant_message=build_assistant_tool_message(),
                tool_messages=[
                    PromptMessage(
                        role="assistant",
                        tool_call_id="call-1",
                        content="invalid",
                    ),
                    PromptMessage(
                        role="tool",
                        tool_call_id="call-2",
                        content='{"result": 2}',
                    ),
                ],
            )

    def test_tool_exchange_rejects_missing_call_ids(self):
        with self.assertRaisesRegex(
            ValidationError,
            "tool call ids are required",
        ):
            ToolExchange(
                assistant_message=PromptMessage(
                    role="assistant",
                    tool_calls=[
                        {
                            "type": "function",
                            "function": {
                                "name": "tool-1",
                                "arguments": "{}",
                            },
                        }
                    ],
                ),
                tool_messages=[PromptMessage(role="tool", content="result")],
            )


if __name__ == "__main__":
    unittest.main()
