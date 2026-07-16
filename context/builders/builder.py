import json

from common.models import PromptMessage
from memory.models import ShortTermMemory
from rag.models import SearchResult


REFERENCE_SEPARATOR = "\n------------------------------\n"


class ContextBuilder:
    def __init__(self,
                 system_prompt: str,
                 session_summary_template: str,
                 rag_reference_context_template: str,
                 rag_reference_item_template: str):
        if not system_prompt:
            raise ValueError("system_prompt is required")
        if not session_summary_template:
            raise ValueError("session_summary_template is required")
        if not rag_reference_context_template:
            raise ValueError("rag_reference_context_template is required")
        if not rag_reference_item_template:
            raise ValueError("rag_reference_item_template is required")

        self.system_prompt = system_prompt
        self.session_summary_template = session_summary_template
        self.rag_reference_context_template = rag_reference_context_template
        self.rag_reference_item_template = rag_reference_item_template

    def build_initial_context(self,
                              user_input: str,
                              short_memory: ShortTermMemory) -> list[PromptMessage]:
        system_content = self.system_prompt
        summary = short_memory.summary
        if summary:
            summary_context = self.session_summary_template.format(
                summary=summary,
            )
            system_content = f"{system_content}\n\n{summary_context}"

        prompts = [
            PromptMessage(role="system", content=system_content)
        ]

        for msg in short_memory.recent_messages:
            if msg.role not in ("assistant", "user"):
                continue
            prompts.append(PromptMessage(role=msg.role, content=msg.content))

        prompts.append(PromptMessage(role="user", content=user_input))
        return prompts

    def build_tool_result_message(self,
                                  call_id: str,
                                  data: dict) -> PromptMessage:
        if not call_id:
            raise ValueError("call_id is required")

        try:
            content = json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError) as error:
            raise ValueError("tool result must be JSON serializable") from error

        return PromptMessage(
            role="tool",
            tool_call_id=call_id,
            content=content,
        )

    def build_rag_context_message(self,
                                  results: list[SearchResult]) -> PromptMessage | None:
        if not results:
            return None

        references = []
        for index, result in enumerate(results, start=1):
            references.append(self.rag_reference_item_template.format(
                index=index,
                source=result.chunk.metadata.source,
                score=f"{result.score:.2f}",
                content=result.chunk.content,
            ))

        content = self.rag_reference_context_template.format(
            references=REFERENCE_SEPARATOR.join(references),
        )
        return PromptMessage(role="system", content=content)
