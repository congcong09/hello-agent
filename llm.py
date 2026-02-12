import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()


class HelloAgentLLM:
    def __init__(
        self,
        model: str | None = None,
        apiKey: str | None = None,
        baseUrl: str | None = None,
        timeout: int | None = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_NAME")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        env_timeout = os.getenv("LLM_TIMEOUT")
        if (timeout is None) and (env_timeout is not None):
            timeout = int(env_timeout)

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError(".env 文件中未定义模型信息")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: list[ChatCompletionMessageParam], temperature: float = 0):
        print(f"正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model or "qwen-plus",
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            print()

            print("LLM 响应成功")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API 是出错: {e}")
            return None


if __name__ == "__main__":
    try:
        llmClient = HelloAgentLLM()
        exampleMessages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes Python code.",
            },
            {"role": "user", "content": "写一个快速排序算法"},
        ]

        print("---- 调用 LLM ----")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n --- 完整模型响应 ---")
            print(responseText)
    except ValueError as e:
        print(e)
