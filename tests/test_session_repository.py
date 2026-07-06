import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from session.repository import SessionRepository


class SessionRepositoryTest(unittest.TestCase):
    def test_find_all_session_ids_returns_ids_from_session_file_names(self):
        with TemporaryDirectory() as temp_dir:
            session_dir = Path(temp_dir) / "session"
            session_dir.mkdir()
            (session_dir / "session-2.json").write_text("not loaded", encoding="utf-8")
            (session_dir / "session-1.json").write_text("not loaded", encoding="utf-8")
            (session_dir / "ignored.txt").write_text("ignored", encoding="utf-8")

            with patch.dict("os.environ", {"STORE_DIR": temp_dir}, clear=False):
                repository = SessionRepository()

                session_ids = repository.find_all_session_ids()

        self.assertEqual(session_ids, ["session-1", "session-2"])

    def test_find_all_session_ids_returns_empty_list_when_session_dir_missing(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"STORE_DIR": temp_dir}, clear=False):
                repository = SessionRepository()

                session_ids = repository.find_all_session_ids()

        self.assertEqual(session_ids, [])


if __name__ == "__main__":
    unittest.main()
