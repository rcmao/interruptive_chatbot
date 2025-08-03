#!/usr/bin/env python3
"""
测试新的工作流管理器
验证完整的工作流：检测时机 → 选择策略 → 生成GPT提示 → 获取插话内容
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.workflow_manager import WorkflowManager
from datetime import datetime

async def test_workflow():
    """测试完整工作流"""
    print("🧪 开始测试新的工作流管理器...")
    
    workflow = WorkflowManager()
    
    # 测试场景1：女性被打断
    print("\n📋 测试场景1：女性被打断")
    conversation1 = [
        ("马龙的反手太稳定了", "Alex", "male"),
        ("我觉得王楚钦的...", "Lily", "female"),
        ("不对，应该是这样", "Zack", "male"),
    ]
    
    for i, (msg, author, gender) in enumerate(conversation1):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
        result = await workflow.process_message(msg, author, gender)
        
        if result.should_intervene:
            print(f"✅ 工作流决定干预")
            print(f"   触发类型: {result.trigger_type}")
            print(f"   策略: {result.strategy}")
            print(f"   建议干预: {result.suggested_intervention}")
            print(f"   推理: {result.reasoning}")
            print(f"   GPT提示长度: {len(result.gpt_prompt) if result.gpt_prompt else 0} 字符")
        else:
            print(f"❌ 工作流决定不干预")
            print(f"   推理: {result.reasoning}")
    
    # 测试场景2：女性被忽视
    print("\n📋 测试场景2：女性被忽视")
    conversation2 = [
        ("这个战术很有效", "Alex", "male"),
        ("我觉得我们可以考虑观众反馈", "Lily", "female"),
        ("继续讨论技术实现", "Zack", "male"),
    ]
    
    for i, (msg, author, gender) in enumerate(conversation2):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
        result = await workflow.process_message(msg, author, gender)
        
        if result.should_intervene:
            print(f"✅ 工作流决定干预")
            print(f"   触发类型: {result.trigger_type}")
            print(f"   策略: {result.strategy}")
            print(f"   建议干预: {result.suggested_intervention}")
            print(f"   推理: {result.reasoning}")
        else:
            print(f"❌ 工作流决定不干预")
            print(f"   推理: {result.reasoning}")
    
    # 测试场景3：男性主导对话
    print("\n📋 测试场景3：男性主导对话")
    conversation3 = [
        ("这个分析很准确", "Alex", "male"),
        ("完全同意", "Zack", "male"),
        ("从技术角度分析...", "Alex", "male"),
    ]
    
    for i, (msg, author, gender) in enumerate(conversation3):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
        result = await workflow.process_message(msg, author, gender)
        
        if result.should_intervene:
            print(f"✅ 工作流决定干预")
            print(f"   触发类型: {result.trigger_type}")
            print(f"   策略: {result.strategy}")
            print(f"   建议干预: {result.suggested_intervention}")
            print(f"   推理: {result.reasoning}")
        else:
            print(f"❌ 工作流决定不干预")
            print(f"   推理: {result.reasoning}")
    
    # 测试场景4：攻击性语境
    print("\n📋 测试场景4：攻击性语境")
    conversation4 = [
        ("这个想法很有创意", "Lily", "female"),
        ("你懂什么？你只是看脸", "Alex", "male"),
    ]
    
    for i, (msg, author, gender) in enumerate(conversation4):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
        result = await workflow.process_message(msg, author, gender)
        
        if result.should_intervene:
            print(f"✅ 工作流决定干预")
            print(f"   触发类型: {result.trigger_type}")
            print(f"   策略: {result.strategy}")
            print(f"   建议干预: {result.suggested_intervention}")
            print(f"   推理: {result.reasoning}")
        else:
            print(f"❌ 工作流决定不干预")
            print(f"   推理: {result.reasoning}")
    
    # 显示工作流状态
    print("\n📊 工作流状态:")
    status = workflow.get_workflow_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # 显示触发类型映射
    print("\n🎯 触发类型映射:")
    trigger_mapping = workflow.get_trigger_type_mapping()
    for trigger, description in trigger_mapping.items():
        print(f"   {trigger}: {description}")
    
    # 显示策略映射
    print("\n🎨 策略映射:")
    strategy_mapping = workflow.get_strategy_mapping()
    for strategy, description in strategy_mapping.items():
        print(f"   {strategy}: {description}")
    
    print("\n🎉 工作流测试完成！")

async def test_gpt_prompt_generation():
    """测试GPT提示生成"""
    print("\n🧪 测试GPT提示生成...")
    
    from src.interventions.gpt_prompt_generator import GPTPromptGenerator, ConversationContext, TriggerType, TKIStrategy
    
    prompt_generator = GPTPromptGenerator()
    
    # 测试提示生成
    context = ConversationContext(
        recent_messages=[
            {"speaker": "Alex", "message": "马龙的反手太稳定了"},
            {"speaker": "Lily", "message": "我觉得王楚钦的..."},
            {"speaker": "Zack", "message": "不对，应该是这样"}
        ],
        trigger_type=TriggerType.FEMALE_INTERRUPTED,
        strategy=TKIStrategy.COMPETING
    )
    
    prompt = prompt_generator.generate_prompt(context)
    print(f"生成的GPT提示:\n{prompt}")
    
    # 显示提示模板信息
    print("\n📋 提示模板信息:")
    info = prompt_generator.get_prompt_template_info()
    for key, value in info.items():
        if key != "description":
            print(f"   {key}: {value}")

if __name__ == '__main__':
    asyncio.run(test_workflow())
    asyncio.run(test_gpt_prompt_generation()) 