import os

from dotenv import load_dotenv

from tools.tool_registry import ToolRegistry


class LlmClientConfig:
    def __init__(self, base_url: str, model: str, api_key: str, max_tokens: int):
        load_dotenv()
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens

        # self.base_url = os.getenv("BASE_URL", "https://integrate.api.nvidia.com/v1")
        # self.model = os.getenv("MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
        # self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
        # self.api_key = os.getenv("API_KEY")
        # self.max_loop = int(os.getenv("MAX_LOOP", 5))
        # self.provider = os.getenv("PROVIDER", "openai")