from rag.rag import build_rag
from tools.impl.tool_collections import QueryBookList, SearchTool
from tools.tool_registry import ToolRegistry


def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.add_tool(QueryBookList())
    registry.add_tool(SearchTool(build_rag()))
    return registry
