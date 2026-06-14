from agent.agent import BaseAgent
from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry


class DemoAgent(BaseAgent):

    def __init__(self,
                 name: str,
                 client: LlmClient,
                 registry: ToolRegistry):
        super().__init__(name, client, registry)


    def run(self, user_input: str) -> str:
        return ""

