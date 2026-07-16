from openai.types.chat import ChatCompletionMessageFunctionToolCall

from agent.agent import BaseAgent
from common.models import PromptMessage
from context.builders.builder import ContextBuilder
from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry
from trace.trace import AgentTrace


class DemoAgent(BaseAgent):

    def __init__(self,
                 name: str,
                 client: LlmClient,
                 registry: ToolRegistry,
                 context_builder: ContextBuilder):
        super().__init__(name, 10, client, registry, 5)
        self.context_builder = context_builder

    def run(self, user_input: str, session_id: str) -> str:
        if not user_input or not user_input.strip():
            raise Exception("No user input")

        trace = AgentTrace(user_input)
        self.last_trace = trace
        session = self.get_session(session_id)
        prompts = self.context_builder.build_initial_context(
            user_input,
            session.short_memory,
        )
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
                execution = self.execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                )
                trace_item = {
                    "name": execution.name,
                    "arguments": execution.arguments,
                }
                if execution.result.get("success") is False:
                    trace_item["error"] = execution.result["error"]
                else:
                    trace_item["result"] = execution.result
                trace.add_tool_call(trace_item)

                prompts.append(self.context_builder.build_tool_result_message(
                    tool_call.id,
                    execution.result,
                ))

        trace.add_final_ans(ans or "")
        return ans or ""
