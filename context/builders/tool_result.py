import json

from context.models import PromptMessage


def build_tool_result_message(call_id: str, data: dict) -> PromptMessage:
    return PromptMessage(
        role="tool",
        tool_call_id=call_id,
        content=json.dumps(data, ensure_ascii=False),
    )
