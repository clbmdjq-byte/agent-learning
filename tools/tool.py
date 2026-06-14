from abc import ABC, abstractmethod

from tools.tool_utils import to_schema


class BaseTool(ABC):
    def __init__(self,
                 name: str,
                 description: str,
                 parameters: dict):
        self.name = name
        self.description = description
        self.parameters = parameters

    @abstractmethod
    def execute(self, params: dict) -> dict:
        pass

    # 先固定openai协议后续再分适配器
    def to_schema(self):
        to_schema(self.name, self.description, self.parameters)
