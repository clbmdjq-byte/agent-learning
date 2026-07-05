import uuid

from agent.factory import build_agent


def main():
    agent = build_agent()
    session_id = str(uuid.uuid4())
    print("输入 exit、quit、q 或 退出 结束对话")

    while True:
        user_input = input("你：").strip()
        if user_input in {"exit", "quit", "q", "退出"}:
            break
        if not user_input:
            continue

        try:
            answer = agent.run(user_input, session_id)
            print("助手：" + answer)
            if agent.last_trace:
                agent.last_trace.print_trace()
        except Exception as error:
            print(f"执行失败：{error}")


if __name__ == "__main__":
    main()
