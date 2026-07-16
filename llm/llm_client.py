from openai import OpenAI
from openai.types.chat import ChatCompletion

from common.models import PromptMessage
from config.config import LlmClientConfig


class LlmClient:
    def __init__(self, config: LlmClientConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key,
                             base_url=config.base_url)

    def chat(self, prompts: list[PromptMessage], tools: list) -> ChatCompletion:
        messages = [
            prompt.model_dump(exclude_none=True)
            for prompt in prompts
        ]
        return self.client.chat.completions.create(messages=messages,
                                                   tools=tools,
                                                   model=self.config.model,
                                                   max_tokens=self.config.max_tokens
                                                   )
