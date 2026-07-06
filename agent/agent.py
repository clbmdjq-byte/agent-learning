from abc import ABC, abstractmethod
import uuid

from agent.models import Session
from common.time_utils import now_ms
from llm.llm_client import LlmClient
from memory.models import Message
from memory.repository import MessageRepository, ShortTermMemoryRepository
from memory.strategy import ShortTermMemoryStrategy
from session.models import SessionInfo
from session.repository import SessionRepository
from tools.tool_registry import ToolRegistry


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
        self.session_repository = SessionRepository()
        self.session_map: dict[str, Session] = {}

    @abstractmethod
    def run(self, user_input: str, session_id: str) -> str:
        pass

    def get_session(self, session_id: str) -> Session:
        session = self.session_map.get(session_id)
        if session is not None:
            return session

        info = self.session_repository.read(session_id)
        if info is None:
            now = now_ms()
            info = SessionInfo(
                session_id=session_id,
                created_at=now,
                updated_at=now,
            )

        memory = self.short_memory_repository.read(session_id)
        if memory is None:
            memory = self.short_memory_strategy.create_memory(session_id)

        session = Session(id=session_id, short_memory=memory, session_info=info)
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

        # Update short-term memory.
        session = self.get_session(session_id)
        short_memory = session.short_memory
        self.short_memory_strategy.update_memory(short_memory, messages)

        # Persist memory and session info after a successful turn.
        self.short_memory_repository.store(short_memory)
        session.session_info.last_message_id = short_memory.last_message_id
        session.session_info.updated_at = now
        self.session_repository.store(session.session_info)
