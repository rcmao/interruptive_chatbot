"""
测试网络连接和Discord API访问
"""

import asyncio
import aiohttp
import ssl
import certifi
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_discord_connection():
    """测试Discord连接"""
    print("🔍 测试Discord连接...")
    
    # 创建SSL上下文
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    # 创建连接器
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            # 测试Discord API
            async with session.get('https://discord.com/api/v10/gateway') as response:
                if response.status == 200:
                    print("✅ Discord API连接正常")
                    return True
                else:
                    print(f"❌ Discord API响应异常: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Discord连接失败: {e}")
            return False

async def test_openai_connection():
    """测试OpenAI API连接"""
    print("🔍 测试OpenAI API连接...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key or not api_base:
        print("❌ 缺少OpenAI API配置")
        return False
    
    # 创建SSL上下文
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            # 测试OpenAI API
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            test_data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            async with session.post(f"{api_base}/chat/completions", 
                                  json=test_data, headers=headers) as response:
                if response.status == 200:
                    print("✅ OpenAI API连接正常")
                    return True
                else:
                    print(f"❌ OpenAI API响应异常: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ OpenAI连接失败: {e}")
            return False

async def main():
    """主测试函数"""
    print("🌐 开始网络连接测试...")
    
    # 测试Discord连接
    discord_ok = await test_discord_connection()
    
    # 测试OpenAI连接
    openai_ok = await test_openai_connection()
    
    print("\n📊 测试结果:")
    print(f"Discord连接: {'✅ 正常' if discord_ok else '❌ 失败'}")
    print(f"OpenAI连接: {'✅ 正常' if openai_ok else '❌ 失败'}")
    
    if discord_ok and openai_ok:
        print("\n�� 所有连接测试通过！可以启动机器人了。")
    else:
        print("\n⚠️ 存在连接问题，请检查网络设置。")

if __name__ == "__main__":
    asyncio.run(main()) 