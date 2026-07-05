from pydantic import BaseModel, Field

from common.types import MessageRole


class Message(BaseModel):
    session_id: str
    message_id: str
    role: MessageRole
    content: str
    created_at: int


class ShortTermMemory(BaseModel):
    session_id: str
    last_message_id: str | None = None
    topic: str = ""
    summary: str = ""
    recent_messages: list[Message] = Field(default_factory=list)
    created_at: int
    updated_at: int
    state: dict = Field(default_factory=dict)

    def add_messages(self, messages: list[Message], updated_at: int) -> None:
        for message in messages:
            self.last_message_id = message.message_id
            self.recent_messages.append(message)
        self.updated_at = updated_at
