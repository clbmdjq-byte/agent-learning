import unittest

from common.models import PromptMessage
from context.builders.builder import ContextBuilder
from context.engine import ContextEngine
from context.models import ContextDraft, ContextWindow, ToolExchange
from context.selectors.selector import NoOpContextSelector
from context.token_estimator import HeuristicTokenEstimator
from memory.models import Message, ShortTermMemory


def build_memory() -> ShortTermMemory:
    return ShortTermMemory(
        session_id="session-1",
        recent_messages=[
            Message(
                session_id="session-1",
                message_id="message-1",
                role="user",
                content="历史问题",
                created_at=1,
            ),
            Message(
                session_id="session-1",
                message_id="message-2",
                role="assistant",
                content="历史回答",
                created_at=2,
            ),
        ],
        created_at=1,
        updated_at=2,
    )


def build_exchange() -> ToolExchange:
    return ToolExchange(
        assistant_message=PromptMessage(
            role="assistant",
            tool_calls=[
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "search", "arguments": "{}"},
                }
            ],
        ),
        tool_messages=[
            PromptMessage(
                role="tool",
                tool_call_id="call-1",
                content='{"data": "result"}',
            )
        ],
    )


class ContextEngineTest(unittest.TestCase):
    def setUp(self):
        self.builder = ContextBuilder(
            system_prompt="system",
            session_summary_template="summary: {summary}",
            rag_reference_context_template="{references}",
            rag_reference_item_template="{content}",
        )

    def build_engine(self):
        return ContextEngine(
            NoOpContextSelector(),
            self.builder,
            HeuristicTokenEstimator(),
            ContextWindow(
                max_context_tokens=1000,
                reserved_output_tokens=100,
                safety_tokens=20,
            ),
        )

    def test_noop_selector_returns_equal_deep_copy(self):
        draft = ContextDraft(
            user_input="当前问题",
            short_memory=build_memory(),
            tool_exchanges=[build_exchange()],
        )

        selected = NoOpContextSelector().select(draft)

        self.assertEqual(draft, selected)
        self.assertIsNot(draft, selected)
        self.assertIsNot(draft.short_memory, selected.short_memory)
        self.assertIsNot(draft.tool_exchanges[0], selected.tool_exchanges[0])

    def test_engine_builds_initial_context_followed_by_complete_exchanges(self):
        engine = self.build_engine()
        draft = ContextDraft(
            user_input="当前问题",
            short_memory=build_memory(),
            tool_exchanges=[build_exchange()],
        )

        tool_schemas = [{"type": "function", "function": {"name": "search"}}]
        result = engine.build(draft, tool_schemas)
        prompts = result.messages

        self.assertEqual(
            ["system", "user", "assistant", "user", "assistant", "tool"],
            [prompt.role for prompt in prompts],
        )
        self.assertEqual("历史问题", prompts[1].content)
        self.assertEqual("历史回答", prompts[2].content)
        self.assertEqual("当前问题", prompts[3].content)
        self.assertEqual("call-1", prompts[5].tool_call_id)
        self.assertGreater(result.usage.system_tokens, 0)
        self.assertGreater(result.usage.tool_schema_tokens, 0)
        self.assertGreater(result.usage.tool_exchange_tokens, 0)

    def test_engine_builds_structured_tool_result_message(self):
        engine = self.build_engine()

        message = engine.build_tool_result_message(
            "call-1",
            {"data": "result"},
        )

        self.assertEqual("tool", message.role)
        self.assertEqual("call-1", message.tool_call_id)
        self.assertEqual('{"data": "result"}', message.content)


if __name__ == "__main__":
    unittest.main()
