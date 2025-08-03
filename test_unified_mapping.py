#!/usr/bin/env python3
"""
测试统一映射 - 验证detectors和interventions之间的逻辑一致性
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.unified_mapping import UnifiedMapping, UnifiedTriggerType, UnifiedTKIStrategy
from src.core.workflow_manager import WorkflowManager
from datetime import datetime

def test_unified_mapping():
    """测试统一映射功能"""
    print("🧪 测试统一映射功能...")
    
    mapping = UnifiedMapping()
    
    # 测试1：触发类型到策略的映射
    print("\n📋 测试1：触发类型到策略的映射")
    test_cases = [
        ("female_interrupted", 5, "高紧急程度"),
        ("female_ignored", 4, "中高紧急程度"),
        ("male_dominance", 3, "中等紧急程度"),
        ("expression_difficulty", 2, "低紧急程度"),
        ("aggressive_context", 5, "高紧急程度")
    ]
    
    for trigger_type, urgency, description in test_cases:
        strategy = mapping.get_strategy_for_trigger(trigger_type, urgency)
        emoji = mapping.get_trigger_emoji(trigger_type)
        print(f"   触发类型: {trigger_type} ({emoji}) - {description}")
        print(f"   选择策略: {strategy.value}")
        print(f"   策略描述: {mapping.get_strategy_description(strategy.value)}")
        print()
    
    # 测试2：转换功能
    print("\n📋 测试2：转换功能")
    
    # 检测器触发类型转换
    detector_triggers = ['female_interrupted', 'silence_after_female', 'male_consecutive']
    for trigger in detector_triggers:
        unified = mapping.convert_detector_trigger(trigger)
        print(f"   检测器: {trigger} -> 统一格式: {unified}")
    
    # GPT触发类型转换
    gpt_triggers = ['❸', '❷', '❶', '❹', '❺']
    for trigger in gpt_triggers:
        unified = mapping.convert_gpt_trigger(trigger)
        print(f"   GPT格式: {trigger} -> 统一格式: {unified}")
    
    # TKI触发类型转换
    tki_triggers = ['structural_marginalization', 'expression_difficulty', 'potential_aggression']
    for trigger in tki_triggers:
        unified = mapping.convert_tki_trigger(trigger)
        print(f"   TKI格式: {trigger} -> 统一格式: {unified}")
    
    # 测试3：获取所有映射
    print("\n📋 测试3：获取所有映射")
    all_mappings = mapping.get_all_mappings()
    print(f"   总映射数量: {len(all_mappings)}")
    
    for trigger, info in all_mappings.items():
        print(f"   {trigger}: {info['emoji']} -> {info['strategy']} (紧急程度: {info['urgency_threshold']})")
    
    print("\n✅ 统一映射测试完成！")

def test_workflow_integration():
    """测试工作流集成"""
    print("\n🧪 测试工作流集成...")
    
    workflow = WorkflowManager()
    
    # 测试场景：女性被打断
    print("\n📋 测试场景：女性被打断")
    conversation = [
        ("马龙的反手太稳定了", "Alex", "male"),
        ("我觉得王楚钦的...", "Lily", "female"),
        ("不对，应该是这样", "Zack", "male"),
    ]
    
    for i, (msg, author, gender) in enumerate(conversation):
        print(f"消息 {i+1}: {author}({gender}): {msg}")
    
    # 模拟检测结果
    print("\n📊 模拟检测结果:")
    print("   触发类型: female_interrupted")
    print("   紧急程度: 5")
    print("   统一映射: female_interrupted -> competing")
    
    # 获取映射信息
    mapping_info = workflow.get_unified_mapping_info()
    print(f"\n📋 统一映射信息:")
    print(f"   总触发类型: {mapping_info['total_triggers']}")
    print(f"   总策略类型: {mapping_info['total_strategies']}")
    
    print("\n✅ 工作流集成测试完成！")

def test_mapping_consistency():
    """测试映射一致性"""
    print("\n🧪 测试映射一致性...")
    
    mapping = UnifiedMapping()
    
    # 测试所有触发类型的一致性
    print("\n📋 测试触发类型一致性:")
    
    # 检测器格式
    detector_formats = ['female_interrupted', 'silence_after_female', 'male_consecutive', 'expression_difficulty', 'aggressive_context']
    
    # GPT格式
    gpt_formats = ['❸', '❷', '❶', '❹', '❺']
    
    # TKI格式
    tki_formats = ['structural_marginalization', 'expression_difficulty', 'potential_aggression']
    
    print("   检测器格式 -> 统一格式:")
    for fmt in detector_formats:
        unified = mapping.convert_detector_trigger(fmt)
        strategy = mapping.get_strategy_for_trigger(unified, 3)
        print(f"     {fmt} -> {unified} -> {strategy.value}")
    
    print("\n   GPT格式 -> 统一格式:")
    for fmt in gpt_formats:
        unified = mapping.convert_gpt_trigger(fmt)
        strategy = mapping.get_strategy_for_trigger(unified, 3)
        print(f"     {fmt} -> {unified} -> {strategy.value}")
    
    print("\n   TKI格式 -> 统一格式:")
    for fmt in tki_formats:
        unified = mapping.convert_tki_trigger(fmt)
        strategy = mapping.get_strategy_for_trigger(unified, 3)
        print(f"     {fmt} -> {unified} -> {strategy.value}")
    
    print("\n✅ 映射一致性测试完成！")

if __name__ == '__main__':
    test_unified_mapping()
    test_workflow_integration()
    test_mapping_consistency() 