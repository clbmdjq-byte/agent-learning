import json

from openai.types.chat import ChatCompletionMessageFunctionToolCall

from agent.agent import BaseAgent
from context.builders import agent_run_context
from context.builders.tool_result import build_tool_result_message
from context.models import PromptMessage
from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry
from trace.trace import AgentTrace


class DemoAgent(BaseAgent):

    def __init__(self,
                 name: str,
                 client: LlmClient,
                 registry: ToolRegistry):
        super().__init__(name, 10, client, registry, 5)

    def run(self, user_input: str, session_id: str) -> str:
        if not user_input or not user_input.strip():
            raise Exception("No user input")

        trace = AgentTrace(user_input)
        self.last_trace = trace
        session = self.get_session(session_id)
        prompts = agent_run_context.build_agent_run_messages(user_input, session.short_memory)
        ans = self.loop(prompts, trace)
        # 构造历史消息，当前先不加入tool_call
        self.after_success(user_input, ans, session_id)
        return ans or ""

    def loop(self, prompts: list[PromptMessage], trace: AgentTrace) -> str:
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
            prompts.append(PromptMessage.model_validate(message.model_dump(exclude_none=True)))

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
                prompts.append(build_tool_result_message(tool_call.id, tool_result))

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
