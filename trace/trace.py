import json
from typing import Any


class AgentTrace:
    def __init__(self, user_input: str):
        self.user_input = user_input
        self.tool_calls = []
        self.final_ans = ""

    def print_trace(self):
        print(self.format())

    def format(self) -> str:
        sections = [
            "========== Agent Trace ==========",
            "[User Input]",
            _format_text(self.user_input),
            "",
            "[Tool Calls]",
            self._format_tool_calls(),
            "",
            "[Final Answer]",
            _format_text(self.final_ans) if self.final_ans else "none",
            "=================================",
        ]
        return "\n".join(sections)

    def _format_tool_calls(self) -> str:
        if not self.tool_calls:
            return "none"

        lines = []
        for index, tool_call in enumerate(self.tool_calls, start=1):
            lines.append(f"{index}. {_format_value(tool_call)}")
        return "\n".join(lines)

    def add_tool_call(self, tool_call: Any):
        self.tool_calls.append(tool_call)

    def add_final_ans(self, final_ans: str):
        self.final_ans = final_ans


def _format_value(value: Any, max_length: int = 800) -> str:
    if isinstance(value, str):
        return _format_text(value, max_length)

    try:
        text = json.dumps(value, ensure_ascii=False, indent=2)
    except TypeError:
        text = str(value)

    return _format_text(text, max_length)


def _format_text(text: str, max_length: int = 800) -> str:
    text = str(text).strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "\n...<truncated>"
