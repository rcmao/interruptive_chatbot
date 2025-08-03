#!/usr/bin/env python3
"""
测试打断检测系统
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.detectors.when_to_interrupt import WhenToInterruptDetector
from src.core.tki_gender_aware_bot import TKIGenderAwareBot
from datetime import datetime

async def test_interruption_detection():
    """测试打断检测系统"""
    print("🧪 开始测试打断检测系统...")
    
    # 测试场景1：性别不平衡
    print("\n📋 测试场景1：性别不平衡")
    detector = WhenToInterruptDetector()
    
    # 模拟男性连续发言
    messages = [
        ("大家好，我是张三", "张三", "male"),
        ("我觉得这个话题很有意思", "张三", "male"),
        ("我们应该深入讨论一下", "张三", "male"),
        ("你们觉得呢？", "张三", "male"),
    ]
    
    for i, (msg, author, gender) in enumerate(messages):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
        decision = detector.analyze_message(msg, author, gender)
        if decision.should_interrupt:
            print(f"✅ 检测到需要干预: {decision.reasoning}")
            print(f"   触发类型: {decision.trigger_type.value}")
            print(f"   紧急程度: {decision.urgency_level}")
            print(f"   置信度: {decision.confidence}")
        else:
            print(f"❌ 未检测到干预需求: {decision.reasoning}")
    
    # 测试场景2：女性表达困难
    print("\n📋 测试场景2：女性表达困难")
    detector2 = WhenToInterruptDetector()
    
    messages2 = [
        ("我觉得...", "李四", "female"),
        ("也许我们可以...", "李四", "female"),
        ("我不太确定，但是...", "李四", "female"),
    ]
    
    for i, (msg, author, gender) in enumerate(messages2):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
        decision = detector2.analyze_message(msg, author, gender)
        if decision.should_interrupt:
            print(f"✅ 检测到需要干预: {decision.reasoning}")
            print(f"   触发类型: {decision.trigger_type.value}")
            print(f"   紧急程度: {decision.urgency_level}")
            print(f"   置信度: {decision.confidence}")
        else:
            print(f"❌ 未检测到干预需求: {decision.reasoning}")
    
    # 测试场景3：TKI机器人完整流程
    print("\n📋 测试场景3：TKI机器人完整流程")
    tki_bot = TKIGenderAwareBot()
    
    # 模拟对话
    conversation = [
        ("这个话题很有意思", "张三", "male"),
        ("我觉得...", "李四", "female"),
        ("你错了，应该是这样", "王五", "male"),
        ("我不太确定", "李四", "female"),
    ]
    
    for i, (msg, author, gender) in enumerate(conversation):
        print(f"\n消息 {i+1}: {author}({gender}): {msg}")
        result = await tki_bot.process_message(msg, author, gender)
        
        if result['should_intervene']:
            print(f"✅ TKI决定干预")
            print(f"   策略: {result['intervention']['strategy']}")
            print(f"   消息: {result['intervention']['message']}")
            print(f"   推理: {result['interruption_decision']['reasoning']}")
        else:
            print(f"❌ TKI决定不干预")
            print(f"   推理: {result['interruption_decision']['reasoning']}")
    
    print("\n🎉 测试完成！")

if __name__ == '__main__':
    asyncio.run(test_interruption_detection()) 