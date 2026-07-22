import json
import math
from abc import ABC, abstractmethod

from common.models import PromptMessage
from context.models import ContextUsage, ContextWindow


MESSAGE_OVERHEAD_TOKENS = 4
TOOL_SCHEMA_OVERHEAD_TOKENS = 8
REQUEST_OVERHEAD_TOKENS = 3


class TokenEstimator(ABC):
    @abstractmethod
    def estimate_text(self, text: str | None) -> int:
        pass

    @abstractmethod
    def estimate(self,
                 messages: list[PromptMessage],
                 tool_schemas: list,
                 window: ContextWindow) -> ContextUsage:
        pass


class HeuristicTokenEstimator(TokenEstimator):
    def estimate_text(self, text: str | None) -> int:
        if not text:
            return 0
        return math.ceil(len(text.encode("utf-8")) / 3)

    def estimate(self,
                 messages: list[PromptMessage],
                 tool_schemas: list,
                 window: ContextWindow) -> ContextUsage:
        system_tokens = 0
        conversation_tokens = 0
        tool_exchange_tokens = 0

        for message in messages:
            tokens = self._estimate_message(message)
            if message.role == "system":
                system_tokens += tokens
            elif message.role == "tool" or (
                message.role == "assistant" and message.tool_calls
            ):
                tool_exchange_tokens += tokens
            else:
                conversation_tokens += tokens

        tool_schema_tokens = sum(
            TOOL_SCHEMA_OVERHEAD_TOKENS + self.estimate_text(
                json.dumps(schema, ensure_ascii=False, sort_keys=True)
            )
            for schema in tool_schemas
        )
        estimated_input_tokens = (
            system_tokens
            + conversation_tokens
            + tool_exchange_tokens
            + tool_schema_tokens
            + REQUEST_OVERHEAD_TOKENS
        )
        estimated_remaining_tokens = (
            window.max_context_tokens
            - window.reserved_output_tokens
            - window.safety_tokens
            - estimated_input_tokens
        )
        return ContextUsage(
            system_tokens=system_tokens,
            conversation_tokens=conversation_tokens,
            tool_exchange_tokens=tool_exchange_tokens,
            tool_schema_tokens=tool_schema_tokens,
            request_overhead_tokens=REQUEST_OVERHEAD_TOKENS,
            estimated_input_tokens=estimated_input_tokens,
            max_context_tokens=window.max_context_tokens,
            reserved_output_tokens=window.reserved_output_tokens,
            safety_tokens=window.safety_tokens,
            estimated_remaining_tokens=estimated_remaining_tokens,
        )

    def _estimate_message(self, message: PromptMessage) -> int:
        tokens = MESSAGE_OVERHEAD_TOKENS + self.estimate_text(message.content)
        if message.tool_calls:
            tokens += self.estimate_text(json.dumps(
                message.tool_calls,
                ensure_ascii=False,
                sort_keys=True,
            ))
        if message.tool_call_id:
            tokens += self.estimate_text(message.tool_call_id)
        return tokens
