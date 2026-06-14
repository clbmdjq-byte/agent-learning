# 先固定openai协议后续再分适配器工具
def build_tool_output(call_id: str, data: dict) -> dict:
    return {
        "call_id": call_id,
        "output": data,
        "type": "function_call_output"
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
