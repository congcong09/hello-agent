import os

from serpapi.google_search import GoogleSearch


def search(query: str) -> str:
    print(f"正在执行 【serpapi】 网页搜索： {query}")

    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("未配置 SERPAPI_API_KEY")

        print(api_key)

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",
            "hl": "zh-cn",
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        print(results)

        # 智能解析:优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i + 1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"未找到关于'{query}'的信息"
    except Exception as e:
        return f"搜索时发生错误 {e}"


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    search("冬奥会")
