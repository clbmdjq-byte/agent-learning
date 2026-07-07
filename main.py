import uuid
import os

from agent.models import Session
from agent.factory import build_agent


def should_print_trace() -> bool:
    return os.getenv("PRINT_TRACE", "").strip().lower() in {"1", "true", "yes", "on"}


def render_session_selector(session_ids: list[str]) -> None:
    print("选择要恢复的会话")
    print("输入编号或 session_id 确认，直接回车或 q 取消")
    print()
    for index, session_id in enumerate(session_ids):
        print(f"{index + 1}. {session_id}")


def select_session_id(session_ids: list[str], input_reader=input) -> str | None:
    if not session_ids:
        print("没有可恢复的会话")
        return None

    message = ""
    while True:
        render_session_selector(session_ids)
        if message:
            print(message)
        command = input_reader("选择：").strip()
        normalized = command.lower()
        message = ""
        if normalized == "" or normalized in {"q", "esc", "exit", "cancel"}:
            return None
        elif normalized.isdigit():
            index = int(normalized) - 1
            if 0 <= index < len(session_ids):
                return session_ids[index]
            message = f"编号超出范围：{command}"
        elif command in session_ids:
            return command
        else:
            message = f"无法识别选择：{command}"


def format_session_preview(session: Session) -> str:
    lines = [f"已恢复 {session.id}"]
    memory = session.short_memory

    if memory.summary:
        lines.extend(["", "[摘要]", memory.summary])

    messages = [
        message
        for message in memory.recent_messages
        if message.role in {"user", "assistant"}
    ]
    if messages:
        lines.extend(["", "[最近上下文]"])
        for message in messages:
            if message.role == "user":
                lines.append(f"> {message.content}")
            else:
                lines.append(message.content)

    return "\n".join(lines)


def main():
    agent = build_agent()
    session_id = str(uuid.uuid4())
    print("输入 /resume 恢复会话，/new 新建会话，exit、quit、q 或 退出 结束对话")

    while True:
        user_input = input("").strip()
        if user_input in {"exit", "quit", "q", "退出"}:
            break
        if not user_input:
            continue
        if user_input == "/new":
            session_id = str(uuid.uuid4())
            print(f"已切换到新会话 {session_id}")
            continue
        if user_input.startswith("/resume"):
            parts = user_input.split(maxsplit=1)
            if len(parts) == 2:
                selected_session_id = parts[1].strip()
            else:
                session_ids = agent.session_repository.find_all_session_ids()
                selected_session_id = select_session_id(session_ids)

            if selected_session_id is None:
                continue

            session = agent.resume_session(selected_session_id)
            if session is None:
                print(f"未找到会话 {selected_session_id}")
                continue

            session_id = session.id
            print(format_session_preview(session))
            continue

        try:
            answer = agent.run(user_input, session_id)
            print(answer)
            if should_print_trace() and agent.last_trace:
                agent.last_trace.print_trace()
        except Exception as error:
            print(f"执行失败：{error}")


if __name__ == "__main__":
    main()
