from abc import ABC, abstractmethod


class BaseTool(ABC):
    def __init__(self,
                 name: str,
                 description: str,
                 parameters: dict):
        self.name = name
        self.description = description
        self.parameters = parameters

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        pass

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
