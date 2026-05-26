from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# 存储掌握度数据 (内存中，生产环境可改用数据库)
# 初始默认掌握度为0
mastery_data = {
    "变量": 0.0,
    "循环": 0.0,
    "函数": 0.0,
    "类": 0.0,
    "文件操作": 0.0
}

@app.route('/')
def index():
    """提供前端页面"""
    return app.send_static_file('knowledge_map.html')

@app.route('/api/update', methods=['POST'])
def update_mastery():
    """更新单个知识点的掌握度"""
    data = request.get_json()
    node_name = data.get('node_name')
    mastery = data.get('mastery')      # 期望0~1之间的浮点数
    if node_name in mastery_data:
        mastery_data[node_name] = float(mastery)
        return jsonify({"status": "success", "message": f"{node_name} 掌握度更新为 {mastery}"})
    else:
        return jsonify({"status": "error", "message": "知识点不存在"}), 400

@app.route('/api/get_status', methods=['GET'])
def get_status():
    """返回所有知识点的掌握度"""
    return jsonify(mastery_data)

@app.route('/api/all_nodes', methods=['GET'])
def get_all_nodes():
    """返回节点列表及初始位置（可选，供前端初始化）"""
    nodes_info = [
        {"name": "变量", "position": [-2, 1, 0]},
        {"name": "循环", "position": [0, 1, 0]},
        {"name": "函数", "position": [2, 1, 0]},
        {"name": "类", "position": [-1, -1, 0]},
        {"name": "文件操作", "position": [1, -1, 0]}
    ]
    return jsonify(nodes_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from agents.planner_agent import plan_path

@app.route('/api/replan', methods=['POST'])
def replan():
    """接收前端传来的已掌握知识点列表，返回新的学习路径"""
    data = request.get_json()
    goal = data.get('goal', '学习Python编程基础')
    mastered = data.get('mastered', [])   # 已掌握的知识点名称列表
    try:
        steps = plan_path(goal, mastered_topics=mastered)
        return jsonify({"status": "success", "steps": steps})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500