from common.store import LocalFileStore
from session.models import SessionInfo


class SessionRepository:
    def __init__(self, store: LocalFileStore | None = None):
        self.store_service = store or LocalFileStore()
        self.base_dir = "session"

    def store(self, session: SessionInfo) -> None:
        if session is None:
            return
        session_id = session.session_id
        file_name = f"{self.base_dir}/{session_id}.json"
        self.store_service.write_text(file_name, session.model_dump_json(indent=2))

    def read(self, session_id: str) -> SessionInfo | None:
        if not session_id:
            return None
        file_name = f"{self.base_dir}/{session_id}.json"
        session = self.store_service.read_text(file_name)
        if session is None:
            return None
        return SessionInfo.model_validate_json(session)

    # Return existing session ids for resume.
    def find_all_session_ids(self) -> list[str]:
        files = self.store_service.list_files(self.base_dir, "*.json")
        return [file.stem for file in files]
