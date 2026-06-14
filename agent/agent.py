from abc import ABC, abstractmethod

from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry

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
                 client: LlmClient,
                 registry: ToolRegistry):
        self.agent_name = name
        self.client = client
        self.tool_registry = registry

    @abstractmethod
    def run(self, user_input: str) -> str:
        pass