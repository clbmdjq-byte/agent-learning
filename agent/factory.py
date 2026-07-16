from agent.agent import BaseAgent
from agent.impl.demo_agent import DemoAgent
from config.config import LlmClientConfig
from context.builders.builder import ContextBuilder
from context.template_loader import load_template
from llm.llm_client import LlmClient
from tools.factory import build_tool_registry


def build_agent() -> BaseAgent:
    config = LlmClientConfig.from_env()
    client = LlmClient(config)
    registry = build_tool_registry()
    context_builder = ContextBuilder(
        system_prompt=load_template("agent_system.txt"),
        session_summary_template=load_template("session_summary.txt"),
        rag_reference_context_template=load_template("rag_reference_context.txt"),
        rag_reference_item_template=load_template("rag_reference_item.txt"),
    )
    return DemoAgent("demo_agent", client, registry, context_builder)
