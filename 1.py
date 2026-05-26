import requests
import json

response = requests.post(
    'http://localhost:11434/api/generate',
    json={'model': 'qwen2:7b', 'prompt': '你好，请用一句话介绍你自己', 'stream': False}
)
result = response.json()
print("LLM输出:", result['response'])