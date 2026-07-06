from pydantic import BaseModel


class SessionInfo(BaseModel):
    session_id: str
    title: str = ""
    created_at: int
    updated_at: int
    last_message_id: str | None = None
