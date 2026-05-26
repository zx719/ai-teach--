import requests
import json

def call_llm(prompt, temperature=0.7):
    """调用本地Ollama模型，返回字符串"""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': 'qwen2:7b', 'prompt': prompt, 'stream': False, 'temperature': temperature}
    )
    return response.json()['response']