import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from agent.agent import BaseAgent


class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__("test", 1, client=None, registry=None, recent_msg_size=10)

    def run(self, user_input: str, session_id: str) -> str:
        return ""


class AgentSessionPersistenceTest(unittest.TestCase):
    def test_get_session_does_not_persist_session_before_successful_turn(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"STORE_DIR": temp_dir}, clear=False):
                agent = TestAgent()

                agent.get_session("session-1")

                self.assertFalse((Path(temp_dir) / "session" / "session-1.json").exists())

    def test_after_success_persists_session_after_one_turn(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"STORE_DIR": temp_dir}, clear=False):
                agent = TestAgent()

                agent.after_success("hello", "hi", "session-1")

                self.assertTrue((Path(temp_dir) / "session" / "session-1.json").exists())


if __name__ == "__main__":
    unittest.main()
