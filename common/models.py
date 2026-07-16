from typing import Any

from pydantic import BaseModel

from common.types import MessageRole


class PromptMessage(BaseModel):
    role: MessageRole
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
