from backend.agents.teacher_agent import generate_question, check_answer

topic = "Python变量"
q = generate_question(topic)
print(q)
ans = input("输入你的答案（A/B/C/D）：")
if check_answer(q, ans):
    print("正确")
else:
    print(f"错误，正确答案是{q['answer']}")