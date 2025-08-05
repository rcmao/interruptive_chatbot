#!/usr/bin/env python3
"""
测试TKI智能干预聊天机器人核心功能
"""

import sys
import os
import asyncio

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.tki_gender_aware_bot import TKIGenderAwareBot

async def main():
    """测试主函数"""
    print("🚀 启动TKI智能干预聊天机器人...")
    
    # 创建机器人实例
    bot = TKIGenderAwareBot()
    
    # 模拟对话
    conversation = [
        ("test1_m", "male", "我觉得这个政策很好，我们应该实施它"),
        ("test2_f", "female", "我...我觉得可能还需要考虑一下其他方面"),
        ("test1_m", "male", "你错了，这个政策很糟糕，你根本不懂"),
        ("test2_f", "female", "但是我想说..."),
        ("test1_m", "male", "别说了，你什么都不懂"),
    ]
    
    print("\n📝 模拟对话:")
    for i, (author, gender, message) in enumerate(conversation):
        print(f"\n{i+1}. {author} ({gender}): {message}")
        
        # 处理消息
        result = await bot.process_message(message, author, gender)
        
        if result.get('should_intervene'):
            intervention = result.get('intervention_message', '')
            strategy = result.get('strategy', '')
            print(f"   🤖 机器人干预 ({strategy}): {intervention}")
    
    # 获取详细分析
    analysis = await bot.get_detailed_analysis()
    print(f"\n📊 对话分析:")
    print(f"   - 总消息数: {analysis.get('total_messages', 0)}")
    print(f"   - 女性消息数: {analysis.get('female_messages', 0)}")
    print(f"   - 男性消息数: {analysis.get('male_messages', 0)}")
    print(f"   - 干预次数: {analysis.get('interventions_count', 0)}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 