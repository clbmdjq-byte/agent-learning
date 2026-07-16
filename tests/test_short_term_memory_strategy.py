import unittest
from types import SimpleNamespace

from memory.models import Message
from memory.strategy import ShortTermMemoryStrategy


class RecordingLlmClient:
    def __init__(self):
        self.prompts = []

    def chat(self, prompts, tools):
        self.prompts.append(prompts)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="更新后的摘要")
                )
            ]
        )


class ShortTermMemoryStrategyTest(unittest.TestCase):
    def setUp(self):
        self.client = RecordingLlmClient()
        self.strategy = ShortTermMemoryStrategy(self.client, 5)
        self.memory = self.strategy.create_memory("session-1")

    def test_five_complete_rounds_are_kept_without_summary(self):
        self.strategy.update_memory(self.memory, build_rounds(1, 5))

        self.assertEqual(10, len(self.memory.recent_messages))
        self.assertEqual([], self.client.prompts)

    def test_sixth_round_summarizes_oldest_complete_round(self):
        self.strategy.update_memory(self.memory, build_rounds(1, 6))

        self.assertEqual(
            [f"user-{index}" for index in range(2, 7)],
            [
                message.content
                for message in self.memory.recent_messages
                if message.role == "user"
            ],
        )
        self.assertEqual(10, len(self.memory.recent_messages))
        self.assertEqual(1, len(self.client.prompts))
        summary_input = self.client.prompts[0][1].content
        self.assertIn("user: user-1", summary_input)
        self.assertIn("assistant: assistant-1", summary_input)
        self.assertNotIn("user: user-2", summary_input)

    def test_legacy_orphan_before_rounds_moves_with_summarized_prefix(self):
        orphan = Message(
            session_id="session-1",
            message_id="orphan-assistant",
            role="assistant",
            content="legacy-orphan",
            created_at=0,
        )
        self.memory.recent_messages.append(orphan)

        self.strategy.update_memory(self.memory, build_rounds(1, 6))

        self.assertEqual("user-2", self.memory.recent_messages[0].content)
        self.assertEqual(10, len(self.memory.recent_messages))
        summary_input = self.client.prompts[0][1].content
        self.assertIn("assistant: legacy-orphan", summary_input)
        self.assertIn("user: user-1", summary_input)
        self.assertIn("assistant: assistant-1", summary_input)


def build_rounds(start: int, count: int) -> list[Message]:
    messages = []
    for index in range(start, start + count):
        messages.extend([
            Message(
                session_id="session-1",
                message_id=f"user-{index}",
                role="user",
                content=f"user-{index}",
                created_at=index,
            ),
            Message(
                session_id="session-1",
                message_id=f"assistant-{index}",
                role="assistant",
                content=f"assistant-{index}",
                created_at=index,
            ),
        ])
    return messages


if __name__ == "__main__":
    unittest.main()
