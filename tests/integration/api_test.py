"""
第三方API配置测试脚本
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_third_party_api():
    """测试第三方API连接"""
    print("🔍 测试第三方API配置...")
    
    # 获取配置
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api2.aigcbest.top/v1")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "❌ API Key 未设置")
    print(f"API Base: {api_base}")
    
    if not api_key:
        print("❌ OPENAI_API_KEY 未在.env文件中设置")
        return False
    
    try:
        # 创建HTTP会话
        async with aiohttp.ClientSession() as session:
            
            # 测试1: 检查API端点是否可访问
            print("\n📡 测试API端点连接...")
            try:
                async with session.get(api_base, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        print("✅ API端点可访问")
                    else:
                        print(f"⚠️  API端点响应状态: {response.status}")
            except Exception as e:
                print(f"❌ API端点连接失败: {e}")
                return False
            
            # 测试2: 尝试调用聊天API
            print("\n🤖 测试聊天API调用...")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "请回复'API测试成功'"}
                ],
                "max_tokens": 20,
                "temperature": 0.1
            }
            
            chat_url = f"{api_base}/chat/completions"
            
            try:
                async with session.post(
                    chat_url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        print(f"✅ API调用成功: {content}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ API调用失败，状态码: {response.status}")
                        print(f"错误信息: {error_text}")
                        return False
                        
            except Exception as e:
                print(f"❌ API调用异常: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def test_discord_config():
    """测试Discord配置"""
    print("\n🤖 检查Discord配置...")
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN 未设置")
        return False
    
    if len(token) < 50:
        print("⚠️  Discord token 长度可能不正确")
        return False
    
    print("✅ Discord token 格式看起来正确")
    return True

def test_system_modules():
    """测试系统模块"""
    print("\n📦 测试系统模块...")
    
    try:
        import discord
        print("✅ discord.py 导入成功")
    except ImportError as e:
        print(f"❌ discord.py 导入失败: {e}")
        return False
    
    try:
        import openai
        print("✅ openai 导入成功")
    except ImportError as e:
        print(f"❌ openai 导入失败: {e}")
        return False
    
    try:
        from main import MessageData, ConflictSignal
        print("✅ 主模块导入成功")
    except ImportError as e:
        print(f"❌ 主模块导入失败: {e}")
        return False
    
    return True

async def test_conflict_detection_with_api():
    """使用真实API测试冲突检测"""
    print("\n🔍 测试冲突检测功能...")
    
    try:
        from main import MultiSignalConflictMonitor, MessageData
        from datetime import datetime
        
        # 创建监控器
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        
        monitor = MultiSignalConflictMonitor(api_key, api_base)
        
        # 创建测试消息
        test_message = MessageData(
            author_id=1,
            author_name="TestUser",
            content="这个想法太荒谬了！",
            timestamp=datetime.now(),
            typing_duration=2.0
        )
        
        # 测试本地功能
        emotion_phrases = monitor.detect_emotion_phrases(test_message.content)
        print(f"✅ 情绪检测: {emotion_phrases}")
        
        # 测试LLM功能（需要API调用）
        print("🔄 测试LLM冲突评分...")
        messages = [f"用户A: 这个方案有问题", f"用户B: 你错了，这样很好"]
        score = await monitor.compute_llm_conflict_score(messages)
        print(f"✅ LLM冲突评分: {score}")
        
        return True
        
    except Exception as e:
        print(f"❌ 冲突检测测试失败: {e}")
        return False

async def run_complete_test():
    """运行完整测试"""
    print("�� 第三方API配置完整测试")
    print("=" * 50)
    
    tests = [
        ("Discord配置", test_discord_config),
        ("系统模块", test_system_modules),
        ("第三方API", test_third_party_api),
        ("冲突检测", test_conflict_detection_with_api),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔄 运行 {test_name} 测试...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results[test_name] = False
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("�� 测试结果总结")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n🚀 下一步:")
        print("1. 启动机器人: python main.py")
        print("2. 在Discord中测试冲突检测功能")
    else:
        print("⚠️  部分测试失败，请检查配置。")
        
        if not results.get("第三方API"):
            print("\n🔧 API问题修复建议:")
            print("- 检查API密钥是否正确")
            print("- 确认API基础URL是否可访问")
            print("- 检查网络连接")
            print("- 尝试更换API服务商")

def create_env_template():
    """创建.env模板"""
    env_content = """# Discord机器人配置
DISCORD_TOKEN=你的Discord机器人令牌

# OpenAI API配置 (第三方服务)
OPENAI_API_KEY=sk-XGGe5y0ZvLcQVFp6XnRizs7q47gsVnAbZx0Xr2mfcVlbr99f
OPENAI_API_BASE=https://api2.aigcbest.top/v1

# 系统配置
CONFLICT_THRESHOLD=0.65
TEST_MODE=false
LOG_LEVEL=INFO
INTERVENTION_COOLDOWN=300
MAX_MESSAGE_HISTORY=10
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("📝 .env 文件已创建，请填入你的Discord Token")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-env":
        create_env_template()
    else:
        asyncio.run(run_complete_test()) 