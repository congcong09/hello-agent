from agent import ReActAgent
from llm import HelloAgentLLM
from tool_executor import ToolExecutor
from tools import search


def run():
    client = HelloAgentLLM()
    tool_executor = ToolExecutor()

    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    # 注册一个 工具
    tool_executor.register("Search", search_description, search)

    agent = ReActAgent(llm_client=client, tool_executor=tool_executor)

    result = agent.run("苹果最新款手机是什么？")

    print(result)


if __name__ == "__main__":
    run()
