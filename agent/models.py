from pydantic import BaseModel

from memory.models import ShortTermMemory
from session.models import SessionInfo


class Session(BaseModel):
    id: str
    short_memory: ShortTermMemory
    session_info: SessionInfo


class ToolExecution(BaseModel):
    name: str
    arguments: dict | str | None
    result: dict
