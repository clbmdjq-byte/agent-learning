from common.models import PromptMessage
from memory.models import Message
from memory.template_loader import load_template


SUMMARY_SYSTEM_PROMPT = load_template("summary_system.txt")
SUMMARY_USER_TEMPLATE = load_template("summary_user.txt")


def build_memory_summary_prompt(old_summary: str,
                                msgs: list[Message]) -> list[PromptMessage]:
    messages_text = _format_messages(msgs)
    return [
        PromptMessage(role="system", content=SUMMARY_SYSTEM_PROMPT),
        PromptMessage(
            role="user",
            content=SUMMARY_USER_TEMPLATE.format(
                old_summary=old_summary or "无",
                messages_text=messages_text or "无",
            ),
        ),
    ]


def _format_messages(msgs: list[Message]) -> str:
    lines = []
    for msg in msgs:
        lines.append(f"{msg.role}: {msg.content}")
    return "\n".join(lines)
