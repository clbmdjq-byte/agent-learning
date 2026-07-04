from tools.tool import BaseTool


class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def add_tool(self, tool: BaseTool):
        if tool.name in self.tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self.tools[tool.name] = tool

    def remove_tool(self, name: str):
        if name in self.tools:
            del self.tools[name]

    def get_tool(self, name: str) -> BaseTool:
        if name in self.tools:
            return self.tools[name]
        else:
            return None

    def tool_schemas(self):
        tool_schemas = []
        for value in self.tools.values():
            if isinstance(value, BaseTool):
                tool_schemas.append(value.to_schema())
        return tool_schemas
