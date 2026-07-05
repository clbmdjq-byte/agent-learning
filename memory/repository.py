from memory.models import Message, ShortTermMemory
from memory.store import LocalFileStore


class MessageRepository:
    def __init__(self, store: LocalFileStore | None = None):
        self.store_service = store or LocalFileStore()
        self.base_dir = "history"

    def store(self, messages: list[Message]) -> None:
        if not messages:
            return

        session_id = messages[0].session_id
        if any(message.session_id != session_id for message in messages):
            raise ValueError("messages must belong to the same session")

        file_name = f"{self.base_dir}/{session_id}.jsonl"
        content = "\n".join(message.model_dump_json() for message in messages)
        self.store_service.append_text(file_name, f"{content}\n")

    def read(self, session_id: str) -> list[Message]:
        file_name = f"{self.base_dir}/{session_id}.jsonl"
        contents = self.store_service.read_lines(file_name)
        messages = []
        for content in contents:
            if content.strip():
                messages.append(Message.model_validate_json(content))
        return messages

class ShortTermMemoryRepository:
    def __init__(self, store: LocalFileStore | None = None):
        self.store_service = store or LocalFileStore()
        self.base_dir = "short_term_memory"

    def store(self, memory: ShortTermMemory) -> None:
        session_id = memory.session_id
        file_name = f"{self.base_dir}/{session_id}.json"
        self.store_service.write_text(file_name, memory.model_dump_json(indent=2))

    def read(self, session_id: str) -> ShortTermMemory | None:
        file_name = f"{self.base_dir}/{session_id}.json"
        content = self.store_service.read_text(file_name)
        if content is None:
            return None
        return ShortTermMemory.model_validate_json(content)

