from pydantic import BaseModel

from memory.models import ShortTermMemory


class Session(BaseModel):
    id: str
    short_memory: ShortTermMemory
