# backend/agents/teacher_agent.py
from ..llm_utils import call_llm
import json

def generate_question(topic):
    prompt = f"""你是一位教师。请根据以下知识点生成一道单项选择题（4个选项）。
知识点：{topic}
要求：
- 题目应考察核心概念。
- 输出必须是严格的JSON格式，不要有任何额外文字。
输出格式示例：
{{"question": "以下哪个是Python变量的正确命名方式？", "options": ["A. 2var", "B. _var", "C. var-name", "D. var name"], "answer": "B"}}
现在生成关于“{topic}”的题目："""
    
    resp = call_llm(prompt, temperature=0.8)
    # 提取JSON（防止模型输出多余解释）
    start = resp.find('{')
    end = resp.rfind('}') + 1
    json_str = resp[start:end]
    return json.loads(json_str)

def check_answer(question_json, student_choice):
    """question_json包含question, options, answer字段，student_choice如'A'"""
    correct = question_json['answer'].strip().upper()
    return student_choice.upper() == correct