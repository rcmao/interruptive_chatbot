import discord
import os
from dotenv import load_dotenv
import openai
from collections import deque
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

class ConflictDetector:
    def __init__(self, api_key, api_base):
        # 配置第三方API
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base  # 使用第三方API地址
        )
        self.message_history = deque(maxlen=8)
        self.intervention_threshold = 7
    
    async def analyze_conflict(self, messages):
        prompt = f"""
你是一个群聊冲突检测AI。请分析以下对话，判断冲突程度（1-10分）：
1-3：正常讨论
4-6：观点分歧，有轻微紧张
7-8：情绪化表达，需要干预
9-10：激烈冲突，急需调解

对话历史：
{chr(10).join(messages)}

请只输出数字分数和简要理由。
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # 或者用 "gpt-3.5-turbo" 更便宜
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return "API调用失败"

# 初始化冲突检测器
detector = ConflictDetector(OPENAI_API_KEY, OPENAI_API_BASE)

@client.event
async def on_ready():
    print(f'Bot 已上线，用户名: {client.user}')
    print("✅ OpenAI 第三方API配置完成")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # 添加消息到历史记录
    detector.message_history.append(f"{message.author}: {message.content}")
    print(f"{message.author}: {message.content}")
    
    # 当有足够消息时进行冲突检测
    if len(detector.message_history) >= 3:
        result = await detector.analyze_conflict(list(detector.message_history))
        print(f"冲突检测结果: {result}")
        
        # 简单判断是否需要干预
        if any(char.isdigit() for char in result):
            try:
                score = int(''.join(filter(str.isdigit, result))[:1])
                if score >= detector.intervention_threshold:
                    await message.channel.send("🤖 我注意到讨论有些激烈，让我们保持冷静，聚焦问题本身。")
            except:
                print("无法解析冲突分数")

client.run(TOKEN)