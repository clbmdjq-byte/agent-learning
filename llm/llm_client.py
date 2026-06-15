from openai import OpenAI
from openai.types.chat import ChatCompletion

from config.config import LlmClientConfig


class LlmClient:
    def __init__(self, config: LlmClientConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key,
                             base_url=config.base_url)

    def chat(self, prompts: list, tools: list) -> ChatCompletion:
        return self.client.chat.completions.create(messages=prompts,
                                                   tools=tools,
                                                   model=self.config.model,
                                                   max_tokens=self.config.max_tokens
                                                   )
