import unittest

from agent.agent import BaseAgent
from tools.tool import BaseTool
from tools.tool_registry import ToolRegistry


class TestAgent(BaseAgent):
    def __init__(self, registry: ToolRegistry):
        super().__init__(
            "test-agent",
            max_loop=1,
            client=None,
            registry=registry,
            recent_msg_size=1,
        )

    def run(self, user_input: str, session_id: str) -> str:
        return ""


class FailingTool(BaseTool):
    def __init__(self):
        super().__init__("failing_tool", "始终执行失败")

    def execute(self, params: dict) -> dict:
        raise RuntimeError("execution failed")


class InvalidResultTool(BaseTool):
    def __init__(self):
        super().__init__("invalid_result_tool", "返回错误类型")

    def execute(self, params: dict) -> dict:
        return "invalid"


class NonSerializableResultTool(BaseTool):
    def __init__(self):
        super().__init__("non_serializable_result_tool", "返回不可序列化内容")

    def execute(self, params: dict) -> dict:
        return {"data": object()}


class AgentToolExecutionTest(unittest.TestCase):
    def setUp(self):
        registry = ToolRegistry()
        registry.add_tool(FailingTool())
        registry.add_tool(InvalidResultTool())
        registry.add_tool(NonSerializableResultTool())
        self.agent = TestAgent(registry)

    def test_missing_tool_returns_error_result(self):
        execution = self.agent.execute_tool("missing_tool", "{}")

        self.assertEqual("tool_not_found", execution.result["error"]["code"])

    def test_invalid_arguments_return_error_result(self):
        execution = self.agent.execute_tool("failing_tool", "not-json")

        self.assertEqual("invalid_arguments", execution.result["error"]["code"])

    def test_non_object_arguments_return_error_result(self):
        execution = self.agent.execute_tool("failing_tool", "[]")

        self.assertEqual("invalid_arguments", execution.result["error"]["code"])

    def test_tool_exception_returns_error_result(self):
        execution = self.agent.execute_tool("failing_tool", "{}")

        self.assertEqual("tool_execution_failed", execution.result["error"]["code"])
        self.assertEqual({}, execution.arguments)

    def test_non_dict_tool_result_returns_error_result(self):
        execution = self.agent.execute_tool("invalid_result_tool", "{}")

        self.assertEqual("invalid_tool_result", execution.result["error"]["code"])

    def test_non_serializable_tool_result_returns_error_result(self):
        execution = self.agent.execute_tool(
            "non_serializable_result_tool",
            "{}",
        )

        self.assertEqual("invalid_tool_result", execution.result["error"]["code"])


if __name__ == "__main__":
    unittest.main()
