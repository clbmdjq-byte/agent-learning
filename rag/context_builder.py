from rag.models import SearchResult


class ContextBuilder:

    def __init__(self):
        self.item_template = """[Reference {index}]
Source: {source}
Score: {score}

Content:
{content}
"""

        self.context_template = """==============================
Reference Documents
==============================

{references}
"""

    def build_context(self, results: list[SearchResult]) -> str:
        if not results:
            return ""

        references = []

        for index, result in enumerate(results, start=1):
            references.append(
                self.item_template.format(
                    index=index,
                    source=result.chunk.metadata.source,
                    score=f"{result.score:.2f}",
                    content=result.chunk.content
                )
            )

        return self.context_template.format(
            references="\n------------------------------\n".join(references)
        )
