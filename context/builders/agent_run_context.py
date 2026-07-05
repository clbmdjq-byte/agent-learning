from context.models import PromptMessage
from memory.models import ShortTermMemory

DEFAULT_SYSTEM_PROMPT = (
    "你是一名问答助手，请使用中文输出并且只输出最终答案"
    "不要输出思考、分析、检索、推理过程。"
)

SUMMARY_CONTEXT_TEMPLATE = """以下是当前会话摘要，用于延续上下文，不是用户的新请求：
{summary}
"""


def build_agent_run_messages(user_input: str,
                             short_memory: ShortTermMemory) -> list[PromptMessage]:
    user_content = f"问题:{user_input}"
    prompts = [
        PromptMessage(role="system", content=DEFAULT_SYSTEM_PROMPT)
    ]
    summary = short_memory.summary
    if summary:
        prompts.append(PromptMessage(role="system", content=SUMMARY_CONTEXT_TEMPLATE.format(summary=summary)))

    recent_msgs = short_memory.recent_messages
    for msg in recent_msgs:
        if msg.role not in ("assistant", "user"):
            continue
        prompts.append(PromptMessage(role=msg.role, content=msg.content))

    prompts.append(PromptMessage(role="user", content=user_content))
    return prompts
