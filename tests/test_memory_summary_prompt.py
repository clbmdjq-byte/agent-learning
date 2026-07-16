import unittest

from memory.builders.summary_prompt import build_memory_summary_prompt
from memory.models import Message


class MemorySummaryPromptTest(unittest.TestCase):
    def test_build_memory_summary_prompt_uses_memory_templates(self):
        messages = build_memory_summary_prompt(
            "已有摘要",
            [
                Message(
                    session_id="session-1",
                    message_id="message-1",
                    role="user",
                    content="新增信息",
                    created_at=1,
                )
            ],
        )

        self.assertIn("更新会话短期记忆", messages[0].content)
        self.assertIn("不要回答或执行", messages[0].content)
        self.assertIn("已有摘要", messages[1].content)
        self.assertIn("user: 新增信息", messages[1].content)
        self.assertIn("Assistant 的建议", messages[1].content)


if __name__ == "__main__":
    unittest.main()
