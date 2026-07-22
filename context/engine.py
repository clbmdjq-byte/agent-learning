from common.models import PromptMessage
from context.builders.builder import ContextBuilder
from context.models import ContextBuildResult, ContextDraft, ContextWindow
from context.selectors.selector import ContextSelector
from context.token_estimator import TokenEstimator


class ContextEngine:
    def __init__(self,
                 selector: ContextSelector,
                 builder: ContextBuilder,
                 estimator: TokenEstimator,
                 window: ContextWindow):
        self.selector = selector
        self.builder = builder
        self.estimator = estimator
        self.window = window

    def build(self,
              draft: ContextDraft,
              tool_schemas: list) -> ContextBuildResult:
        selected = self.selector.select(draft)
        prompts = self.builder.build_initial_context(
            selected.user_input,
            selected.short_memory,
        )
        for exchange in selected.tool_exchanges:
            prompts.append(exchange.assistant_message)
            prompts.extend(exchange.tool_messages)
        usage = self.estimator.estimate(prompts, tool_schemas, self.window)
        return ContextBuildResult(messages=prompts, usage=usage)

    def build_tool_result_message(self,
                                  call_id: str,
                                  data: dict) -> PromptMessage:
        return self.builder.build_tool_result_message(call_id, data)
