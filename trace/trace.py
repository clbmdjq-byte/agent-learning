import json
from typing import Any


class AgentTrace:
    def __init__(self, user_input: str):
        self.user_input = user_input
        self.context_usages = []
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
            "[Context Usage]",
            self._format_context_usages(),
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

    def _format_context_usages(self) -> str:
        if not self.context_usages:
            return "none"

        lines = []
        for index, usage in enumerate(self.context_usages, start=1):
            lines.append(f"{index}. {_format_value(usage)}")
        return "\n".join(lines)

    def add_context_usage(self, usage: Any):
        self.context_usages.append(usage)

    def add_tool_call(self, tool_call: Any):
        self.tool_calls.append(tool_call)

    def add_final_ans(self, final_ans: str):
        self.final_ans = final_ans


def _format_value(value: Any, max_length: int = 800) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump()

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
