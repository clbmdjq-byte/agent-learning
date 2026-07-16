from uuid import uuid4

from common.models import PromptMessage
from common.time_utils import now_ms
from memory.models import Message

HISTORY_MESSAGE_ROLES = {"user", "assistant"}


def convert_to_messages(runtime_msgs: list[PromptMessage], session_id: str) -> list[Message]:
    messages = []
    for runtime_msg in runtime_msgs:
        message = convert_to_message(runtime_msg, session_id)
        if message is not None:
            messages.append(message)
    return messages


def convert_to_message(runtime_msg: PromptMessage, session_id: str) -> Message | None:
    if runtime_msg.role not in HISTORY_MESSAGE_ROLES:
        return None

    if runtime_msg.content is None:
        return None

    return Message(
        session_id=session_id,
        message_id=str(uuid4()),
        role=runtime_msg.role,
        content=runtime_msg.content,
        created_at=now_ms(),
    )
