from typing import Any

from tools import search


class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """

    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}

    def register(self, name: str, description: str, func: callable):
        if name in self.tools:
            print(f"警告: 工具 '{name}' 已存在，将被覆盖!")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册")

    def get(self, name):
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self):
        return "\n".join(
            [f"- {name}: {info['description']}" for name, info in self.tools.items()]
        )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    toolExecutor = ToolExecutor()

    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    # 注册一个 工具
    toolExecutor.register("Search", search_description, search)

    # 打印可用工具
    print("\n---- 可用工具 ----")
    print(toolExecutor.getAvailableTools())

    # 问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.get(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误:未找到名为 '{tool_name}' 的工具。")
