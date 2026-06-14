from urllib import response

from openai import OpenAI
from openai.types.responses import Response

from config.config import LlmClientConfig


class LlmClient:
    def __init__(self, config: LlmClientConfig, tools: list):
        self.config = config
        self.tools = tools
        self.client = OpenAI(api_key=config.api_key,
                             base_url=config.base_url)

    def chat(self, prompts: list) -> Response:
        return self.client.responses.create(input=prompts,
                                            tools=self.tools,
                                            model=self.config.model,
                                            max_output_tokens=self.config.max_tokens)



