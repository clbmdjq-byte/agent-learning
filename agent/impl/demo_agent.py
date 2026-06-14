import json

from openai.types.responses import ResponseFunctionToolCall

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
        prompts = [{"role": "system", "context": "系统提示词"}
            , {"role": "user", "content":"参考资料:XXX;问题:"+user_input }]
        ans = ''
        previous_response_id = None
        for i in range(self.max_loop):
            res = self.client.chat(prompts,
                                   self.tool_registry.tool_list(),
                                   previous_response_id)
            if res is None or res.output is None:
                raise Exception('llm not responding')

            tool_outputs = []
            for o in res.output:
                if o is None or not isinstance(o, ResponseFunctionToolCall):
                    continue
                tool = self.tool_registry.get_tool(o.name)
                if tool is None:
                    print("tool not found:" + o.name)
                    continue
                args = parse_arguments(o.arguments)
                tool_result = tool.execute(args)
                tool_outputs.append(build_tool_output(o.call_id, tool_result))
            if not tool_outputs:
                return res.output_text or ""
            else:
                # todo 组装tool result
                prompts = tool_outputs
        return ans


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
