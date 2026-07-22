from pydantic import BaseModel, Field, field_validator, model_validator

from common.models import PromptMessage
from memory.models import ShortTermMemory


class ToolExchange(BaseModel):
    assistant_message: PromptMessage
    tool_messages: list[PromptMessage]

    @model_validator(mode="after")
    def validate_messages(self) -> "ToolExchange":
        if self.assistant_message.role != "assistant":
            raise ValueError("assistant_message must use assistant role")

        tool_calls = self.assistant_message.tool_calls or []
        if not tool_calls:
            raise ValueError("assistant_message must include tool_calls")

        if any(message.role != "tool" for message in self.tool_messages):
            raise ValueError("tool_messages must use tool role")

        call_ids = [call.get("id") for call in tool_calls]
        result_ids = [message.tool_call_id for message in self.tool_messages]
        if any(not call_id for call_id in call_ids + result_ids):
            raise ValueError("tool call ids are required")

        call_ids.sort()
        result_ids.sort()
        if call_ids != result_ids:
            raise ValueError("tool result ids must match tool call ids")
        return self


class ContextDraft(BaseModel):
    user_input: str
    short_memory: ShortTermMemory
    tool_exchanges: list[ToolExchange] = Field(default_factory=list)

    @field_validator("user_input")
    @classmethod
    def validate_user_input(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("user_input is required")
        return value


class ContextWindow(BaseModel):
    max_context_tokens: int
    reserved_output_tokens: int
    safety_tokens: int

    @field_validator("max_context_tokens")
    @classmethod
    def validate_max_context_tokens(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_context_tokens must be positive")
        return value

    @field_validator("reserved_output_tokens", "safety_tokens")
    @classmethod
    def validate_non_negative_tokens(cls, value: int) -> int:
        if value < 0:
            raise ValueError("token reserves must be non-negative")
        return value


class ContextUsage(BaseModel):
    system_tokens: int
    conversation_tokens: int
    tool_exchange_tokens: int
    tool_schema_tokens: int
    request_overhead_tokens: int
    estimated_input_tokens: int
    max_context_tokens: int
    reserved_output_tokens: int
    safety_tokens: int
    estimated_remaining_tokens: int


class ContextBuildResult(BaseModel):
    messages: list[PromptMessage]
    usage: ContextUsage
