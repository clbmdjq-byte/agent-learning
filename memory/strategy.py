from common.time_utils import now_ms
from llm.llm_client import LlmClient
from memory.builders.summary_prompt import build_memory_summary_prompt
from memory.models import Message, ShortTermMemory

class ShortTermMemoryStrategy:
    def __init__(self, client: LlmClient, recent_msg_size: int):
        self.recent_msg_size = recent_msg_size
        self.client = client


    def create_memory(self, session_id: str) -> ShortTermMemory:
        created_at = now_ms()
        return ShortTermMemory(
            session_id=session_id,
            created_at=created_at,
            updated_at=created_at,
        )

    def update_memory(self,
               memory: ShortTermMemory,
               messages: list[Message]) -> None:
        if not messages:
            return

        memory.add_messages(messages, now_ms())

        # 只按完整的 user -> assistant 轮次裁剪，避免拆散问答。
        cut_msgs = []
        round_starts = _find_complete_round_starts(memory.recent_messages)
        overflow_rounds = len(round_starts) - self.recent_msg_size
        if overflow_rounds > 0:
            cut_size = round_starts[overflow_rounds]
            cut_msgs = memory.recent_messages[:cut_size]
            memory.recent_messages = memory.recent_messages[cut_size:]
        if not cut_msgs:
            return

        # 尝试压缩摘要
        summary_prompt = build_memory_summary_prompt(memory.summary, cut_msgs)
        res = self.client.chat(prompts=summary_prompt, tools=[])
        content = res.choices[0].message.content
        if not content:
            return

        memory.summary = content.strip()
        memory.updated_at = now_ms()


def _find_complete_round_starts(messages: list[Message]) -> list[int]:
    starts = []
    index = 0
    while index < len(messages) - 1:
        current = messages[index]
        following = messages[index + 1]
        if current.role == "user" and following.role == "assistant":
            starts.append(index)
            index += 2
        else:
            index += 1
    return starts
