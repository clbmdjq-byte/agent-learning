import json
from pathlib import Path

from rag.rag import LocalRag
from tools.tool import BaseTool


class QueryBookList(BaseTool):
    def __init__(self):
        super().__init__(
            name="query_book_list",
            description="查询当前个人笔记中记录的可查阅的目录，包括 Agent 学习资料、产品手册、制度文档、旅行攻略、烹饪笔记和运动规则。",
        )

    def execute(self, params: dict) -> dict:
        books_path = Path(__file__).resolve().parent / "query_book_list_mock.json"
        with books_path.open("r", encoding="utf-8") as file:
            books = json.load(file)

        return {
            "data": books,
            "description": "当前个人笔记中记录的可查阅的目录。",
        }


class SearchTool(BaseTool):

    def __init__(self, rag: LocalRag):
        super().__init__(
            name="search_tool",
            description=(
                "检索 Agent 可访问的个人知识、外挂知识库或外部参考资料。"
                "当用户的问题需要依赖已保存的笔记、文档、资料内容或私有知识来回答时调用。"
                "不要用于查询资料目录；如果用户想知道当前有哪些资料、文档列表或知识库目录，应调用 query_book_list。"
            ),
            parameters=SearchTool.parameters()
        )
        self.rag = rag

    @staticmethod
    def parameters() -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "用于检索知识内容的自然语言查询，通常直接使用用户问题或提炼后的关键词。"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }

    def execute(self, params: dict) -> dict:
        results = self.rag.search(params["query"])
        data = []
        for result in results:
            data.append({
                "content": result.chunk.content,
                "source": result.chunk.metadata.source,
                "score": result.score,
            })

        return {
            "data": data,
            "description": "当前命中的参考资料，可用于回答用户问题。"
        }
