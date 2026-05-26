from ..llm_utils import call_llm
import json

def plan_path(goal, mastered_topics=None):
    if mastered_topics is None:
        mastered_topics = []
    prompt = f"""你是学习规划师。用户学习目标：{goal}。
用户已掌握的知识点：{mastered_topics}。
请输出一个学习路径，包含5个必须按顺序学习的知识点步骤（跳过已掌握的）。
**重要：知识点名称必须严格从以下列表中选择：变量, 循环, 函数, 类, 文件操作**
输出格式（JSON）：{{"steps": ["知识点1", "知识点2", "知识点3", "知识点4", "知识点5"]}}
只输出JSON，不要解释。"""
    resp = call_llm(prompt, temperature=0.4)
    # ... 后续解析不变
    start = resp.find('{')
    end = resp.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("规划师输出不包含有效JSON")
    return json.loads(resp[start:end])["steps"]