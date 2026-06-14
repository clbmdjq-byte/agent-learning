import os

from dotenv import load_dotenv


class LlmClientConfig:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model = os.getenv("MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
        self.api_key = os.getenv("API_KEY")
        self.max_loop = int(os.getenv("MAX_LOOP", 5))
        self.provider = os.getenv("PROVIDER","openai")