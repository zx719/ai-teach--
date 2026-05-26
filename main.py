import sys
import os
import requests
import time

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.agents.planner_agent import plan_path
from backend.agents.teacher_agent import generate_question, check_answer
from backend.agents.tutor_agent import explain

# Flask API 地址（根据实际情况修改，如果Flask运行在Windows本机，WSL中需用Windows IP）
FLASK_API_URL = "http://localhost:5000"   # Windows本机运行Flask时使用
# 如果您的 main.py 在 WSL 中运行，Flask 在 Windows 中，请将 localhost 改为 Windows 的 IP
# FLASK_API_URL = "http://172.18.112.1:5000"   # 示例，需自行获取

def update_mastery_to_map(node_name, mastery):
    """调用 Flask API 更新知识点的掌握度"""
    try:
        resp = requests.post(
            f"{FLASK_API_URL}/api/update",
            json={"node_name": node_name, "mastery": mastery},
            timeout=2
        )
        if resp.status_code == 200:
            print(f"  📡 已同步地图：{node_name} 掌握度 = {mastery:.0%}")
        else:
            print(f"  ⚠️ 地图同步失败：{resp.text}")
    except Exception as e:
        print(f"  ❌ 无法连接地图服务：{e}")

def get_current_mastery_from_map():
    """从 Flask 获取当前所有知识点的掌握度（用于重新规划）"""
    try:
        resp = requests.get(f"{FLASK_API_URL}/api/get_status", timeout=2)
        if resp.status_code == 200:
            return resp.json()   # 字典，如 {"变量":0.85, "循环":0.0, ...}
        else:
            print("获取掌握度失败，使用空掌握度")
            return {}
    except Exception as e:
        print(f"无法获取当前掌握度：{e}，将使用空掌握度")
        return {}

def run_learning_cycle(goal):
    # 1. 获取当前掌握度（用于跳过已学内容）
    current_mastery = get_current_mastery_from_map()
    mastered_topics = [topic for topic, score in current_mastery.items() if score >= 0.7]
    
    # 2. 规划学习路径（跳过已掌握）
    steps = plan_path(goal, mastered_topics=mastered_topics)
    print(f"📚 学习路径规划完成：{' → '.join(steps)}")
    
    # 3. 遍历每个知识点
    for idx, topic in enumerate(steps):
        print(f"\n===== 学习知识点 {idx+1}/{len(steps)}：{topic} =====")
        correct_count = 0
        total_attempts = 0
        
        # 每个知识点最多尝试2次（第一次答错可答疑，第二次再错则标记掌握度低）
        for attempt in range(2):
            # 教师出题
            q = generate_question(topic)
            print(f"\n题目：{q['question']}")
            for opt in q['options']:
                print(opt)
            student_ans = input("你的答案（A/B/C/D）：").strip()
            total_attempts += 1
            
            if check_answer(q, student_ans):
                print("✅ 回答正确！")
                correct_count += 1
                break
            else:
                print(f"❌ 错误。正确答案是 {q['answer']}")
                if attempt == 0:
                    explanation = explain(q['question'], q['answer'], student_ans, topic)
                    print(f"\n💡 答疑：{explanation}\n")
                else:
                    print("第二次尝试仍失败，系统将标记此知识点为薄弱。")
        
        # 计算掌握度（简单模型：正确次数/尝试次数）
        mastery = correct_count / total_attempts if total_attempts > 0 else 0
        print(f"知识点「{topic}」掌握度：{mastery:.0%}")
        
        # 4. 立即更新到地图（Flask API）
        update_mastery_to_map(topic, mastery)
        
        # 等待一下，让前端有时间刷新（可选）
        time.sleep(0.5)
    
    print("\n🎉 学习闭环完成！请查看浏览器中的知识地图颜色变化。")

def replan_from_frontend():
    """
    供前端“重新规划”按钮调用的接口（在main.py中独立运行，或集成到Flask中）。
    实际上，重新规划的逻辑已在 run_learning_cycle 中通过获取当前掌握度实现。
    这里提供一个单独的函数，可被Flask路由调用（下一节会添加）。
    """
    current_mastery = get_current_mastery_from_map()
    mastered = [k for k, v in current_mastery.items() if v >= 0.7]
    print("当前已掌握知识点：", mastered)
    goal = input("请输入新的学习目标（或回车使用上次目标）：")
    if not goal:
        goal = "学习Python编程基础"
    new_steps = plan_path(goal, mastered_topics=mastered)
    print("重新规划后的路径：", new_steps)
    return new_steps

if __name__ == "__main__":
    goal = input("请输入学习目标（例如：学习Python编程基础）：")
    run_learning_cycle(goal)