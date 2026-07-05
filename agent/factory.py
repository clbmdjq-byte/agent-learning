from agent.agent import BaseAgent
from agent.impl.demo_agent import DemoAgent
from config.config import LlmClientConfig
from llm.llm_client import LlmClient
from tools.factory import build_tool_registry


def build_agent() -> BaseAgent:
    config = LlmClientConfig.from_env()
    client = LlmClient(config)
    registry = build_tool_registry()
    return DemoAgent("demo_agent", client, registry)
