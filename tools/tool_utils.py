# 先固定openai协议后续再分适配器工具
import json


def build_tool_output(call_id: str, data: dict) -> dict:
    return {
        "role":"tool",
        "tool_call_id": call_id,
        "content": json.dumps(data, ensure_ascii=False)

    }


def to_schema(name: str, description: str, parameters: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }
