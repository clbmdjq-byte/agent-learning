import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageFunctionToolCall,
)

from agent.impl.demo_agent import DemoAgent
from context.builders.builder import ContextBuilder
from context.engine import ContextEngine
from context.models import ContextDraft, ContextWindow
from context.selectors.selector import ContextSelector, NoOpContextSelector
from context.token_estimator import HeuristicTokenEstimator
from tools.tool import BaseTool
from tools.tool_registry import ToolRegistry


class AlwaysRequestToolClient:
    def chat(self, prompts, tools):
        message = ChatCompletionMessage(
            role="assistant",
            content=None,
            tool_calls=[
                ChatCompletionMessageFunctionToolCall(
                    id="call-1",
                    type="function",
                    function={
                        "name": "test_tool",
                        "arguments": "{}",
                    },
                )
            ],
        )
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message)],
        )


class SequencedClient:
    def __init__(self, messages):
        self.messages = iter(messages)
        self.calls = []

    def chat(self, prompts, tools):
        self.calls.append(list(prompts))
        return SimpleNamespace(
            choices=[SimpleNamespace(message=next(self.messages))],
        )


class TestTool(BaseTool):
    def __init__(self):
        super().__init__("test_tool", "用于测试循环耗尽")

    def execute(self, params: dict) -> dict:
        return {"success": True}


class RecordingSelector(ContextSelector):
    def __init__(self):
        self.call_count = 0

    def select(self, draft: ContextDraft) -> ContextDraft:
        self.call_count += 1
        return draft.model_copy(deep=True)


class DemoAgentTest(unittest.TestCase):
    def build_agent(self, client, registry, selector=None):
        context_engine = ContextEngine(
            selector or NoOpContextSelector(),
            ContextBuilder(
                system_prompt="system",
                session_summary_template="summary: {summary}",
                rag_reference_context_template="{references}",
                rag_reference_item_template="{content}",
            ),
            HeuristicTokenEstimator(),
            ContextWindow(
                max_context_tokens=1000,
                reserved_output_tokens=100,
                safety_tokens=20,
            ),
        )
        return DemoAgent(
            name="test-agent",
            client=client,
            registry=registry,
            context_engine=context_engine,
        )

    def test_tool_loop_persists_and_can_be_restored_by_new_agent(self):
        tool_call_message = ChatCompletionMessage(
            role="assistant",
            content=None,
            tool_calls=[
                ChatCompletionMessageFunctionToolCall(
                    id="call-1",
                    type="function",
                    function={
                        "name": "test_tool",
                        "arguments": "{}",
                    },
                )
            ],
        )
        final_message = ChatCompletionMessage(
            role="assistant",
            content="已根据工具完成回答",
        )
        registry = ToolRegistry()
        registry.add_tool(TestTool())

        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"STORE_DIR": temp_dir}, clear=False):
                first_client = SequencedClient([tool_call_message, final_message])
                selector = RecordingSelector()
                first_agent = self.build_agent(first_client, registry, selector)

                answer = first_agent.run("请调用工具回答", "session-1")

                self.assertEqual("已根据工具完成回答", answer)
                self.assertEqual(2, selector.call_count)
                self.assertEqual(2, len(first_agent.last_trace.context_usages))
                self.assertEqual(
                    0,
                    first_agent.last_trace.context_usages[0].tool_exchange_tokens,
                )
                self.assertGreater(
                    first_agent.last_trace.context_usages[1].tool_exchange_tokens,
                    0,
                )
                tool_result = first_client.calls[1][-1]
                self.assertEqual("tool", tool_result.role)
                self.assertEqual("call-1", tool_result.tool_call_id)
                self.assertIn('"success": true', tool_result.content)

                restored_client = SequencedClient([
                    ChatCompletionMessage(role="assistant", content="继续回答")
                ])
                restored_agent = self.build_agent(restored_client, registry)

                restored_session = restored_agent.resume_session("session-1")
                self.assertIsNotNone(restored_session)

                restored_answer = restored_agent.run("继续", "session-1")

                self.assertEqual("继续回答", restored_answer)
                restored_prompts = restored_client.calls[0]
                self.assertEqual(
                    ["system", "user", "assistant", "user"],
                    [prompt.role for prompt in restored_prompts],
                )
                self.assertEqual("请调用工具回答", restored_prompts[1].content)
                self.assertEqual("已根据工具完成回答", restored_prompts[2].content)
                self.assertEqual("继续", restored_prompts[3].content)

    def test_run_raises_and_does_not_persist_when_max_loop_exhausted(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"STORE_DIR": temp_dir}, clear=False):
                registry = ToolRegistry()
                registry.add_tool(TestTool())
                agent = self.build_agent(AlwaysRequestToolClient(), registry)
                agent.max_loop = 1

                with self.assertRaisesRegex(
                    RuntimeError,
                    "agent loop exhausted after 1 iterations",
                ):
                    agent.run("需要持续调用工具", "session-1")

                store_dir = Path(temp_dir)
                self.assertFalse((store_dir / "history" / "session-1.jsonl").exists())
                self.assertFalse((store_dir / "short_term_memory" / "session-1.json").exists())
                self.assertFalse((store_dir / "session" / "session-1.json").exists())


if __name__ == "__main__":
    unittest.main()
