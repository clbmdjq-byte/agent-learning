import unittest

from rag.models import Chunk, Metadata, SearchResult
from tools.impl.tool_collections import SearchTool


class FakeRag:
    def search(self, query: str) -> list[SearchResult]:
        return [
            SearchResult(
                chunk=Chunk(
                    content=f"命中内容：{query}",
                    chunk_id="chunk-1",
                    metadata=Metadata(source="context.md"),
                ),
                score=0.9,
                retrieval_source="common",
            )
        ]


class SearchToolTest(unittest.TestCase):
    def test_execute_converts_search_results_to_tool_dict(self):
        tool = SearchTool(FakeRag())

        result = tool.execute({"query": "Context Engineering"})

        self.assertEqual(
            result["data"],
            [
                {
                    "content": "命中内容：Context Engineering",
                    "source": "context.md",
                    "score": 0.9,
                }
            ],
        )
        self.assertIn("参考资料", result["description"])


if __name__ == "__main__":
    unittest.main()
