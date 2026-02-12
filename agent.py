import re

from openai.types.chat import ChatCompletionMessageParam

from llm import HelloAgentLLM
from tool_executor import ToolExecutor

REACT_PROMPT_TEMPLATE = """
请注意:你是一个有能力调用外部工具的只能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:
Thought:你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action:你决定采取的行动，必须是以下格式之一:
  - `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
  - `Finish[最终答案]`:当你认为已经获得最终答案时。
  - 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

请开始解决以下问题:
  Question:{question}
  History: {history}
"""


class ReActAgent:
    def __init__(
        self, llm_client: HelloAgentLLM, tool_executor: ToolExecutor, max_steps: int = 5
    ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        运行 ReAct 智能体来回答一个问题
        """

        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第{current_step}步 ---")

            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)

            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc, question=question, history=history_str
            )

            messages: list[ChatCompletionMessageParam] = [
                {"role": "user", "content": prompt}
            ]
            response_text = self.llm_client.think(messages)

            if not response_text:
                print("错误:LLM未能返回有效响应。")
                break

            thought, action = self._parse_output(response_text)

            if thought:
                print(f"思考：{thought}")
            if not action:
                print("警告：未能解析出有效的Action，终止流程。")
                break
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print(f"🎉 最终答案：{final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # TODO: 处理无效的 action 问题
                continue

            print(f"🎬 行动：{tool_name}[{tool_input}]")

            tool_function = self.tool_executor.get(tool_name)

            if not tool_function:
                observation = f"错误:未找到名为'{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input)

            print(f"👀 观察:{observation}")

            # 将本轮的 Action 和 Observation 添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("已达到最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)

        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """
        解析action字符串，提取工具名称和输入。
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None


if __name__ == "__main__":
    pass
