import unittest
from io import StringIO
from unittest.mock import patch

from agent.models import Session
from memory.models import Message, ShortTermMemory
from session.models import SessionInfo
from main import (
    format_session_preview,
    render_session_selector,
    select_session_id,
    should_print_trace,
)


class MainCliTest(unittest.TestCase):
    def test_format_session_preview_uses_short_memory_without_assistant_prefix(self):
        session = Session(
            id="session-1",
            session_info=SessionInfo(session_id="session-1", created_at=1, updated_at=2),
            short_memory=ShortTermMemory(
                session_id="session-1",
                summary="讨论了 CLI resume 流程。",
                recent_messages=[
                    Message(
                        session_id="session-1",
                        message_id="m1",
                        role="user",
                        content="如何恢复会话？",
                        created_at=1,
                    ),
                    Message(
                        session_id="session-1",
                        message_id="m2",
                        role="assistant",
                        content="可以使用短期记忆展示预览。",
                        created_at=2,
                    ),
                ],
                created_at=1,
                updated_at=2,
            ),
        )

        preview = format_session_preview(session)

        self.assertIn("已恢复 session-1", preview)
        self.assertIn("讨论了 CLI resume 流程。", preview)
        self.assertIn("> 如何恢复会话？", preview)
        self.assertIn("可以使用短期记忆展示预览。", preview)
        self.assertNotIn("助手：", preview)

    def test_select_session_id_returns_none_on_cancel(self):
        with patch("main.render_session_selector"):
            selected = select_session_id(["session-1"], lambda _: "q")

        self.assertIsNone(selected)

    def test_select_session_id_returns_session_by_number(self):
        with patch("main.render_session_selector"):
            selected = select_session_id(["session-1", "session-2"], lambda _: "2")

        self.assertEqual(selected, "session-2")

    def test_select_session_id_returns_session_by_id(self):
        with patch("main.render_session_selector"):
            selected = select_session_id(["session-1", "session-2"], lambda _: "session-2")

        self.assertEqual(selected, "session-2")

    def test_select_session_id_retries_after_invalid_number(self):
        commands = iter(["3", "1"])

        with patch("main.render_session_selector"), patch("sys.stdout", StringIO()):
            selected = select_session_id(["session-1", "session-2"], lambda _: next(commands))

        self.assertEqual(selected, "session-1")

    def test_render_session_selector_lists_numbered_sessions(self):
        output = StringIO()

        with patch("sys.stdout", output):
            render_session_selector(["session-1", "session-2"])

        rendered = output.getvalue()
        self.assertIn("1. session-1", rendered)
        self.assertIn("2. session-2", rendered)
        self.assertNotIn("\033[7m", rendered)

    def test_should_print_trace_is_false_by_default(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(should_print_trace())

    def test_should_print_trace_accepts_enabled_env_values(self):
        for value in ["1", "true", "yes", "on"]:
            with self.subTest(value=value):
                with patch.dict("os.environ", {"PRINT_TRACE": value}, clear=True):
                    self.assertTrue(should_print_trace())


if __name__ == "__main__":
    unittest.main()
