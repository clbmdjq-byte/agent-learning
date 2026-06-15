import json
from pathlib import Path

from tools.tool import BaseTool


class QueryBookList(BaseTool):
    def __init__(self):
        super().__init__(name="query_book_list",
                         description="查询当前图书馆可借阅和有库存的书籍列表")

    def execute(self, params: dict) -> dict:
        books_path = Path(__file__).resolve().parent / "query_book_list_mock.json"
        with books_path.open("r", encoding="utf-8") as file:
            books = json.load(file)

        return {
            "data": books,
            "description": "当前图书馆可借阅和有库存的书籍列表"
        }
