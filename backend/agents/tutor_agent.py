from ..llm_utils import call_llm

def explain(question, correct_answer, student_answer, topic):
    prompt = f"""学生做错了一道关于“{topic}”的题目。
题目：{question}
正确答案：{correct_answer}
学生回答：{student_answer}
请用通俗易懂的语言解释为什么学生答案错误，并给出一个记忆技巧或易混淆点对比。
输出要简洁、鼓励性。"""
    return call_llm(prompt, temperature=0.7)