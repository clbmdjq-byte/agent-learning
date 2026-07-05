from rag.models import SearchResult


REFERENCE_ITEM_TEMPLATE = """[Reference {index}]
Source: {source}
Score: {score}

Content:
{content}
"""

REFERENCE_CONTEXT_TEMPLATE = """==============================
Reference Documents
==============================

{references}
"""

REFERENCE_SEPARATOR = "\n------------------------------\n"


class RagResultFormatter:
    def build_context(self, results: list[SearchResult]) -> str:
        if not results:
            return ""

        references = [
            self._format_result(index, result)
            for index, result in enumerate(results, start=1)
        ]

        return REFERENCE_CONTEXT_TEMPLATE.format(
            references=REFERENCE_SEPARATOR.join(references)
        )

    def _format_result(self, index: int, result: SearchResult) -> str:
        return REFERENCE_ITEM_TEMPLATE.format(
            index=index,
            source=result.chunk.metadata.source,
            score=f"{result.score:.2f}",
            content=result.chunk.content
        )
