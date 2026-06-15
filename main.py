import os

from dotenv import load_dotenv

from agent.impl.demo_agent import DemoAgent
from config.config import LlmClientConfig
from llm.llm_client import LlmClient
from tools.impl.query_book_list import QueryBookList
from tools.tool_registry import ToolRegistry


def build_agent() -> DemoAgent:
    load_dotenv()

    config = LlmClientConfig(
        base_url=os.getenv("BASE_URL",""),
        model=os.getenv("MODEL",""),
        api_key=os.getenv("API_KEY",""),
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
    )
    client = LlmClient(config)
    registry = ToolRegistry()
    registry.add_tool(QueryBookList())
    return DemoAgent("demo_agent", client, registry)


def main():
    agent = build_agent()
    print("输入 exit、quit、q 或 退出 结束对话")

    while True:
        user_input = input("你：").strip()
        if user_input in {"exit", "quit", "q", "退出"}:
            break
        if not user_input:
            continue

        try:
            answer = agent.run(user_input)
            print("助手：" + answer)
        except Exception as error:
            print(f"执行失败：{error}")


if __name__ == "__main__":
    main()
