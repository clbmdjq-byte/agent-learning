from common.time_utils import now_ms
from context.builders.memory_summary import build_memory_summary_prompt
from llm.llm_client import LlmClient
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

        # 判断是否满足N轮了满足后进行裁剪更新
        cut_msgs = []
        size = len(memory.recent_messages)
        if size > self.recent_msg_size:
            cut_size = size - self.recent_msg_size
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
