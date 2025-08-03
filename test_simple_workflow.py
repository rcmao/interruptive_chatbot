#!/usr/bin/env python3
"""
简单测试工作流管理器
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.workflow_manager import WorkflowManager

async def test_workflow():
    """测试工作流管理器"""
    
    print("🧪 测试工作流管理器...")
    print("=" * 50)
    
    # 创建工作流管理器实例
    workflow = WorkflowManager()
    
    # 测试场景：女性被打断
    print("\n📝 测试场景：女性被打断")
    print("-" * 30)
    
    # 模拟对话历史 - 包含更多消息来触发干预
    test_messages = [
        ("Lily", "female", "大家好，我想分享一下我的想法..."),
        ("Alex", "male", "好的，请说"),
        ("Lily", "female", "我觉得这个问题可以从另一个角度来考虑..."),
        ("Alex", "male", "不对，你说得不对，应该是这样..."),
        ("Alex", "male", "而且我觉得你的想法太简单了"),
        ("Zack", "male", "我同意Alex的观点"),
        ("Alex", "male", "看吧，大家都这么认为"),
        ("Lily", "female", "但是我觉得..."),
        ("Alex", "male", "别说了，你的观点没有道理")
    ]
    
    for i, (username, gender, message) in enumerate(test_messages, 1):
        print(f"\n消息 {i}:")
        print(f"  发送者: {username} ({gender})")
        print(f"  内容: {message}")
        
        # 处理消息
        result = await workflow.process_message(message, username, gender)
        
        print(f"  分析结果:")
        print(f"    是否需要干预: {result.should_intervene}")
        if result.should_intervene:
            print(f"    策略: {result.strategy}")
            print(f"    触发类型: {result.trigger_type}")
            print(f"    置信度: {result.confidence}")
            print(f"    建议干预: {result.suggested_intervention}")
            print(f"    推理: {result.reasoning}")
            print("🎯 触发干预！")
        else:
            print(f"    原因: {result.reasoning}")
    
    print("\n" + "=" * 50)
    print("🏁 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_workflow()) 