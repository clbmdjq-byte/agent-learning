import os

from dotenv import load_dotenv

from agent.agent import BaseAgent
from agent.impl.demo_agent import DemoAgent
from config.config import LlmClientConfig
from llm.llm_client import LlmClient
from tools.factory import build_tool_registry


def build_agent() -> BaseAgent:
    load_dotenv()

    config = LlmClientConfig(
        base_url=os.getenv("BASE_URL", ""),
        model=os.getenv("MODEL", ""),
        api_key=os.getenv("API_KEY", ""),
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
    )
    client = LlmClient(config)
    registry = build_tool_registry()
    return DemoAgent("demo_agent", client, registry)
