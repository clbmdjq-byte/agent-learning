import json

from openai.types.chat import ChatCompletionMessageFunctionToolCall

from agent.agent import BaseAgent
from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry
from tools.tool_utils import build_tool_output
from trace.trace import AgentTrace


class DemoAgent(BaseAgent):

    def __init__(self,
                 name: str,
                 client: LlmClient,
                 registry: ToolRegistry):
        super().__init__(name, 10, client, registry)

    def run(self, user_input: str) -> str:
        if not user_input or not user_input.strip():
            raise Exception("No user input")

        trace = AgentTrace(user_input)
        self.last_trace = trace

        user_content = f"问题:{user_input}"
        prompts = [
            {"role": "system", "content": "你是一名问答助手，请使用中文输出并且只输出最终答案不要输出思考、分析、检索、推理过程。"},
            {"role": "user", "content": user_content},
        ]

        ans = ""
        for _ in range(self.max_loop):
            res = self.client.chat(prompts,
                                   self.tool_registry.tool_schemas())
            if res is None or not res.choices:
                raise Exception("llm not responding")

            message = res.choices[0].message
            tool_calls = message.tool_calls or []
            if not tool_calls:
                ans = message.content
                break
            prompts.append(message.model_dump(exclude_none=True))

            for tool_call in tool_calls:
                if not isinstance(tool_call, ChatCompletionMessageFunctionToolCall):
                    continue
                tool = self.tool_registry.get_tool(tool_call.function.name)
                if tool is None:
                    trace.add_tool_call({
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                        "error": "tool not found",
                    })
                    continue
                args = parse_arguments(tool_call.function.arguments)
                tool_result = tool.execute(args)
                trace.add_tool_call({
                    "name": tool_call.function.name,
                    "arguments": args,
                    "result": tool_result,
                })
                prompts.append(build_tool_output(tool_call.id, tool_result))

        trace.add_final_ans(ans or "")
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
