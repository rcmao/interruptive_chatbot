#!/usr/bin/env python3
"""
测试机器人启动
"""

import sys
import os

# 添加src到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def test_imports():
    """测试导入"""
    print("�� 测试导入...")
    
    try:
        from core.explainable_system import ExplainableInterventionBot
        print("  ✅ ExplainableInterventionBot 导入成功")
    except ImportError as e:
        print(f"  ❌ ExplainableInterventionBot 导入失败: {e}")
        return False
    
    try:
        from core.main import IntelligentConflictBot
        print("  ✅ IntelligentConflictBot 导入成功")
    except ImportError as e:
        print(f"  ❌ IntelligentConflictBot 导入失败: {e}")
        return False
    
    return True

def test_bot_creation():
    """测试机器人创建"""
    print("\n�� 测试机器人创建...")
    
    try:
        from core.explainable_system import ExplainableInterventionBot
        bot = ExplainableInterventionBot()
        print("  ✅ ExplainableInterventionBot 创建成功")
        return True
    except Exception as e:
        print(f"  ❌ ExplainableInterventionBot 创建失败: {e}")
        return False

def test_message_processing():
    """测试消息处理"""
    print("\n📨 测试消息处理...")
    
    try:
        from core.explainable_system import ExplainableInterventionBot
        import asyncio
        
        async def test():
            bot = ExplainableInterventionBot()
            result = await bot.process_message_with_explanation(
                "我觉得你的想法完全错误！", 
                "测试用户", 
                "test_channel"
            )
            if result:
                print(f"  ✅ 干预生成: {result[:50]}...")
            else:
                print("  ✅ 无需干预")
            return True
        
        asyncio.run(test())
        return True
    except Exception as e:
        print(f"  ❌ 消息处理失败: {e}")
        return False

if __name__ == "__main__":
    print("�� 开始测试...")
    
    success = True
    success &= test_imports()
    success &= test_bot_creation()
    success &= test_message_processing()
    
    if success:
        print("\n✨ 所有测试通过！机器人可以正常启动。")
        print("\n💡 现在可以运行: python main.py")
    else:
        print("\n❌ 测试失败，请检查代码。") 