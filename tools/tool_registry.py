from tools.tool import BaseTool
from tools.impl.query_metric_list import QueryMetricList


class ToolRegistry:

    def __init__(self):
        self.tools = {}
        self.add_tool(QueryMetricList())

    def add_tool(self, tool: BaseTool):
        if tool.name in self.tools:
            print("tool already registered")
            return
        self.tools[tool.name] = tool

    def remove_tool(self, name: str):
        if name in self.tools:
            del self.tools[name]

    def get_tool(self, name: str) -> BaseTool:
        if name in self.tools:
            return self.tools[name]
        else:
            return None

    def tool_list(self):
        return list(self.tools.values())
