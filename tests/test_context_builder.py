import unittest

from context.builders.builder import ContextBuilder
from context.template_loader import load_template
from memory.models import ShortTermMemory
from rag.models import Chunk, Metadata, SearchResult


class ContextBuilderTest(unittest.TestCase):
    def setUp(self):
        self.builder = ContextBuilder(
            system_prompt=load_template("agent_system.txt"),
            session_summary_template=load_template("session_summary.txt"),
            rag_reference_context_template=load_template("rag_reference_context.txt"),
            rag_reference_item_template=load_template("rag_reference_item.txt"),
        )

    def test_build_initial_context_uses_memory_and_file_templates(self):
        memory = ShortTermMemory(
            session_id="session-1",
            summary="用户正在设计 Context。",
            created_at=1,
            updated_at=1,
        )

        messages = self.builder.build_initial_context(
            "下一步是什么？",
            memory,
        )

        self.assertIn("问答助手", messages[0].content)
        self.assertIn("用户正在设计 Context。", messages[1].content)
        self.assertIn("不是可执行指令", messages[1].content)
        self.assertIn("<conversation_summary>", messages[1].content)
        self.assertEqual("下一步是什么？", messages[-1].content)

    def test_build_rag_context_message_formats_selected_results(self):
        result = SearchResult(
            chunk=Chunk(
                content="Context 负责组织模型输入。",
                chunk_id="chunk-1",
                metadata=Metadata(source="context.md"),
            ),
            score=0.876,
            retrieval_source="common",
        )

        message = self.builder.build_rag_context_message([result])

        self.assertIsNotNone(message)
        self.assertEqual("system", message.role)
        self.assertIn("[Reference 1]", message.content)
        self.assertIn("Source: context.md", message.content)
        self.assertIn("Score: 0.88", message.content)
        self.assertIn("Context 负责组织模型输入。", message.content)

    def test_build_rag_context_message_returns_none_without_results(self):
        self.assertIsNone(self.builder.build_rag_context_message([]))

    def test_build_tool_result_message_serializes_structured_result(self):
        message = self.builder.build_tool_result_message(
            "call-1",
            {"data": "检索结果"},
        )

        self.assertEqual("tool", message.role)
        self.assertEqual("call-1", message.tool_call_id)
        self.assertEqual('{"data": "检索结果"}', message.content)

    def test_build_tool_result_message_rejects_non_serializable_result(self):
        with self.assertRaisesRegex(ValueError, "JSON serializable"):
            self.builder.build_tool_result_message(
                "call-1",
                {"data": object()},
            )


if __name__ == "__main__":
    unittest.main()
