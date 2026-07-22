from openai.types.chat import ChatCompletionMessageFunctionToolCall

from agent.agent import BaseAgent
from common.models import PromptMessage
from context.engine import ContextEngine
from context.models import ContextDraft, ToolExchange
from llm.llm_client import LlmClient
from tools.tool_registry import ToolRegistry
from trace.trace import AgentTrace


class DemoAgent(BaseAgent):

    def __init__(self,
                 name: str,
                 client: LlmClient,
                 registry: ToolRegistry,
                 context_engine: ContextEngine):
        super().__init__(name, 10, client, registry, 5)
        self.context_engine = context_engine

    def run(self, user_input: str, session_id: str) -> str:
        if not user_input or not user_input.strip():
            raise Exception("No user input")

        trace = AgentTrace(user_input)
        self.last_trace = trace
        session = self.get_session(session_id)
        draft = ContextDraft(
            user_input=user_input,
            short_memory=session.short_memory,
        )
        ans = self.loop(draft, trace)
        # 构造历史消息，当前先不加入tool_call
        self.after_success(user_input, ans, session_id)
        return ans or ""

    def loop(self, draft: ContextDraft, trace: AgentTrace) -> str:
        ans = ""
        for _ in range(self.max_loop):
            tool_schemas = self.tool_registry.tool_schemas()
            context_result = self.context_engine.build(draft, tool_schemas)
            trace.add_context_usage(context_result.usage)
            res = self.client.chat(context_result.messages, tool_schemas)
            if res is None or not res.choices:
                raise Exception("llm not responding")

            message = res.choices[0].message
            tool_calls = message.tool_calls or []
            if not tool_calls:

                ans = message.content
                break
            assistant_message = PromptMessage.model_validate(
                message.model_dump(exclude_none=True)
            )
            tool_messages = []

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

                tool_messages.append(
                    self.context_engine.build_tool_result_message(
                        tool_call.id,
                        execution.result,
                    )
                )
            draft.tool_exchanges.append(ToolExchange(
                assistant_message=assistant_message,
                tool_messages=tool_messages,
            ))
        else:
            raise RuntimeError(
                f"agent loop exhausted after {self.max_loop} iterations"
            )

        trace.add_final_ans(ans or "")
        return ans or ""
