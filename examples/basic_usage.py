#!/usr/bin/env python3
"""
基本使用示例 - 展示如何使用中断式聊天机器人
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.main import InterruptiveBot
from src.detectors.context_aware_detector import ContextAwareDetector
from src.interventions.intervention_generator import InterventionGenerator

def main():
    """基本使用示例"""
    print("🚀 启动中断式聊天机器人...")
    
    # 初始化检测器
    detector = ContextAwareDetector()
    
    # 初始化干预生成器
    intervention_gen = InterventionGenerator()
    
    # 创建机器人实例
    bot = InterruptiveBot(
        detector=detector,
        intervention_generator=intervention_gen
    )
    
    # 模拟对话
    conversation = [
        "用户A: 我觉得这个政策很好",
        "用户B: 你错了，这个政策很糟糕",
        "用户A: 你才错了，你根本不懂",
        "用户B: 你是个白痴"
    ]
    
    print("\n📝 模拟对话:")
    for message in conversation:
        print(f"  {message}")
        
        # 检测是否需要干预
        should_intervene = bot.detect_interruption(message)
        
        if should_intervene:
            intervention = bot.generate_intervention(message)
            print(f"  🤖 机器人干预: {intervention}")
    
    print("\n✅ 示例完成!")

if __name__ == "__main__":
    main() 