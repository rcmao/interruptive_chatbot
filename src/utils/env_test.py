"""
测试环境变量加载
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("🔍 检查环境变量:")
print(f"DISCORD_TOKEN: {os.getenv('DISCORD_TOKEN')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE')}") 