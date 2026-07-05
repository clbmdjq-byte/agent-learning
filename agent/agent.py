import uuid
from abc import ABC, abstractmethod

from agent.models import Session
from common.time_utils import now_ms
from llm.llm_client import LlmClient
from memory.models import ShortTermMemory, Message
from memory.repository import MessageRepository, ShortTermMemoryRepository
from memory.strategy import ShortTermMemoryStrategy
from tools.tool_registry import ToolRegistry
from trace.trace import AgentTrace


# BaseAgent
#
# 当前仅实现 DemoAgent，验证：
# LLM、Tool Calling、Memory、RAG
#
# 后续执行模式：
# ChatAgent        - 问答
# ToolLoopAgent    - 工具循环
# ReactAgent       - ReAct
# PlanExecuteAgent - 计划执行
# MultiAgent       - 多 Agent 协作
#
# Agent 能力 = Prompt + ToolRegistry + Memory + RAG

class BaseAgent(ABC):
    def __init__(self,
                 name: str,
                 max_loop: int,
                 client: LlmClient,
                 registry: ToolRegistry,
                 recent_msg_size: int):
        self.agent_name = name
        self.max_loop = max_loop
        self.client = client
        self.tool_registry = registry
        self.last_trace = None
        self.short_memory_strategy = ShortTermMemoryStrategy(client, recent_msg_size)
        self.message_repository = MessageRepository()
        self.short_memory_repository = ShortTermMemoryRepository()
        self.session_map = {}

    @abstractmethod
    def run(self, user_input: str, session_id: str) -> str:
        pass

    def get_session(self, session_id: str) -> Session:
        session = self.session_map.get(session_id)
        if not session:
            memory = self.short_memory_repository.read(session_id)
            if memory:
                session = Session(id=session_id, short_memory=memory)
            else:
                memory = self.short_memory_strategy.create_memory(session_id)
                session = Session(id=session_id, short_memory=memory)
            self.session_map[session_id] = session
        return session




    def after_success(self,
                      user_input: str,
                      llm_ans: str,
                      session_id: str) -> None:
        now = now_ms()
        messages = [
            Message(session_id=session_id,
                    message_id=str(uuid.uuid4()),
                    role="user",
                    content=user_input,
                    created_at=now),
            Message(session_id=session_id,
                    message_id=str(uuid.uuid4()),
                    role="assistant",
                    content=llm_ans,
                    created_at=now),
        ]
        self.message_repository.store(messages)

        ## 更新短期记忆
        session = self.get_session(session_id)
        short_memory = session.short_memory
        self.short_memory_strategy.update_memory(short_memory, messages)
        # 持久化短期记忆
        self.short_memory_repository.store(short_memory)
