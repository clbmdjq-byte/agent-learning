from context.models import PromptMessage
from memory.models import Message


SUMMARY_SYSTEM_PROMPT = (
    "你是会话短期记忆摘要器。"
    "你只根据输入内容更新摘要，只输出摘要正文，不要输出 Markdown 代码块。"
)

SUMMARY_USER_TEMPLATE = """
请根据【已有摘要】和【新增对话片段】更新短期记忆摘要。

要求：
1. 只保留对后续对话有用的信息。
2. 保留用户确认的设计决策、架构约束、命名、流程、待澄清问题。
3. 删除寒暄、重复解释、临时推理过程。
4. 不要加入新增对话中没有出现的信息。
5. 如果新增对话修正了已有摘要，以新增对话为准。
6. 摘要使用中文，尽量压缩但不要丢失关键决策。
7. 只输出更新后的摘要正文，不要解释处理过程，不要使用 Markdown 代码块。

【已有摘要】
{old_summary}

【新增对话片段】
{messages_text}

【输出】
更新后的前置摘要正文
""".strip()


def build_memory_summary_prompt(old_summary: str, msgs: list[Message]) -> list[PromptMessage]:
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
