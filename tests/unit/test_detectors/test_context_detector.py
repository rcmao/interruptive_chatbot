#!/usr/bin/env python3
"""
本地测试上下文冲突检测系统
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加src到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from core.main import ContextualConflictDetector, format_score_bar

def test_conflict_scenarios():
    """测试多种冲突场景"""
    
    detector = ContextualConflictDetector()
    
    # 测试场景1：排练冲突（您提到的例子）
    scenario1 = [
        ("Ruochen Mao", "我们今天排练第三次了，你能不能这次按PPT内容来讲？"),
        ("小明", "昨天老师点名我们超时了……"),
        ("Ruochen Mao", "但那是因为你讲太久，我临场讲两句就顺带收尾了。"),
        ("小明", "我觉得讲稿念出来太死板了。"),
        ("Ruochen Mao", "可是我们需要控制时间啊，不然又要被老师批评"),
        ("小明", "那你觉得应该怎么办？")
    ]
    
    # 测试场景2：作业分工冲突
    scenario2 = [
        ("Alice", "大家好，讨论一下作业分工"),
        ("Bob", "我这边可以负责前面部分"),
        ("Alice", "你上次说的前面部分到现在还没做完吗？"),
        ("Bob", "我这几天比较忙，马上就做"),
        ("Alice", "你总是说忙，但是deadline就要到了！"),
        ("Bob", "我知道，但我真的很忙，你能不能理解一下")
    ]
    
    # 测试场景3：正常对话（不应该干预）
    scenario3 = [
        ("张三", "今天天气不错呢"),
        ("李四", "是的，适合出去走走"),
        ("张三", "我们一起去公园吧"),
        ("李四", "好主意，几点出发？")
    ]
    
    scenarios = [
        ("排练时间冲突", scenario1),
        ("作业分工争议", scenario2), 
        ("正常日常对话", scenario3)
    ]
    
    for scenario_name, conversation in scenarios:
        print(f"\n{'='*60}")
        print(f"🎭 测试场景: {scenario_name}")
        print(f"{'='*60}")
        
        # 重置检测器
        detector = ContextualConflictDetector()
        
        for speaker, message in conversation:
            print(f"\n💬 {speaker}: {message}")
            
            result = detector.add_message(speaker, message)
            
            # 显示分析结果
            timestamp = datetime.now().strftime('%H:%M:%S')
            status = "🚨" if result.should_intervene else "✅"
            score_bar = format_score_bar(result.conflict_score)
            
            print(f"""
{status} [{timestamp}] 轮次#{len(detector.conversation_history)}
📊 冲突分数: {result.conflict_score:.2f} {score_bar}
🔍 冲突模式: {result.pattern.value if result.pattern else '无'}
🎯 推荐策略: {result.strategy.value}
💭 分析依据: {result.reasoning}
            """.strip())
            
            if result.should_intervene:
                print(f"🤖 干预建议: {result.intervention_message}")
            
            print("-" * 50)

def interactive_test():
    """交互式测试"""
    print("\n🧪 交互式冲突检测测试")
    print("=" * 50)
    print("输入对话来测试系统响应（输入'quit'退出）")
    print("格式: 姓名: 消息内容")
    print("例如: Alice: 我觉得你的想法有问题")
    print()
    
    detector = ContextualConflictDetector()
    
    while True:
        try:
            user_input = input("💬 请输入对话: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 测试结束")
                break
            
            if ':' not in user_input:
                print("❌ 格式错误，请使用 '姓名: 消息' 格式")
                continue
            
            speaker, message = user_input.split(':', 1)
            speaker = speaker.strip()
            message = message.strip()
            
            if not speaker or not message:
                print("❌ 姓名和消息不能为空")
                continue
            
            # 分析消息
            result = detector.add_message(speaker, message)
            
            # 显示结果
            timestamp = datetime.now().strftime('%H:%M:%S')
            status = "🚨" if result.should_intervene else "✅" 
            score_bar = format_score_bar(result.conflict_score)
            
            print(f"""
{status} [{timestamp}] {speaker} (轮次#{len(detector.conversation_history)})
📊 冲突分数: {result.conflict_score:.2f} {score_bar}
🔍 冲突模式: {result.pattern.value if result.pattern else '无'}
🎯 推荐策略: {result.strategy.value}
💭 {result.reasoning}
            """.strip())
            
            if result.should_intervene:
                print(f"🤖 机器人干预: {result.intervention_message}")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 测试结束")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

def main():
    """主测试函数"""
    print("🤖 上下文冲突检测系统测试")
    print("=" * 60)
    
    while True:
        print("\n请选择测试模式:")
        print("1. 预设场景测试")
        print("2. 交互式测试") 
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == '1':
            test_conflict_scenarios()
        elif choice == '2':
            interactive_test()
        elif choice == '3':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请输入1-3")

if __name__ == "__main__":
    main() 