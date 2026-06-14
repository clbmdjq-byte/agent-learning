from openai import OpenAI
from openai.types.responses import Response

from config.config import LlmClientConfig


class LlmClient:
    def __init__(self, config: LlmClientConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key,
                             base_url=config.base_url)

    def chat(self, prompts: list, tools: list, previous_response_id: str | None) -> Response:
        return self.client.responses.create(input=prompts,
                                            tools=tools,
                                            model=self.config.model,
                                            max_output_tokens=self.config.max_tokens,
                                            previous_response_id=previous_response_id
                                            )
