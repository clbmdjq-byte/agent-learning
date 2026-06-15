import json

from openai.types.chat import ChatCompletionMessageFunctionToolCall

from agent.agent import BaseAgent
from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry
from tools.tool_utils import *


class DemoAgent(BaseAgent):

    def __init__(self,
                 name: str,
                 client: LlmClient,
                 registry: ToolRegistry):
        super().__init__(name, 10, client, registry)

    def run(self, user_input: str) -> str:
        if not user_input or not user_input.strip():
            raise Exception('No user input')

        ## todo 召回知识库、记忆等相关信息组成最终prompts,也可以作为tool由agent负责调用先简单实现chain模式
        prompts = [{"role": "system", "content": "你是一名问数助手"}
            , {"role": "user", "content":"参考资料:X;问题:"+user_input }]
        ans = ""
        for i in range(self.max_loop):
            res = self.client.chat(prompts,
                                   self.tool_registry.tool_schemas())
            if res is None or not res.choices:
                raise Exception('llm not responding')

            message = res.choices[0].message
            tool_calls = message.tool_calls or []
            if not tool_calls:
                ans = message.content
                break
            prompts.append(message.model_dump(exclude_none=True))

            for o in tool_calls:
                if not isinstance(o, ChatCompletionMessageFunctionToolCall):
                    continue
                tool = self.tool_registry.get_tool(o.function.name)
                if tool is None:
                    print("tool not found:" + o.function.name)
                    continue
                args = parse_arguments(o.function.arguments)
                tool_result = tool.execute(args)
                prompts.append(build_tool_output(o.id, tool_result))

        return ans or ""


def parse_arguments(arguments) -> dict:
    if arguments is None:
        return {}

    if isinstance(arguments, str):
        return json.loads(arguments)

    if isinstance(arguments, dict):
        return arguments

    raise ValueError(
        f"unsupported arguments type: {type(arguments)}"
    )
