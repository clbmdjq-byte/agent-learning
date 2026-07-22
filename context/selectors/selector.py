from abc import ABC, abstractmethod

from context.models import ContextDraft


class ContextSelector(ABC):
    @abstractmethod
    def select(self, draft: ContextDraft) -> ContextDraft:
        pass


class NoOpContextSelector(ContextSelector):
    def select(self, draft: ContextDraft) -> ContextDraft:
        return draft.model_copy(deep=True)
