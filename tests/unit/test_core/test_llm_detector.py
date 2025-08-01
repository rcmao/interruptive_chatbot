#!/usr/bin/env python3
"""
测试GPT-4冲突检测系统
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加src到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from core.llm_detector import GPT4ConflictAnalyzer, format_score_bar, get_color_indicator

async def test_llm_scenarios():
    """测试LLM检测场景"""
    
    analyzer = GPT4ConflictAnalyzer()
    
    # 测试场景1：明显的攻击性语言
    scenario1 = [
        ("用户A", "我觉得你真的有毛病"),
        ("用户B", "哈麻批"),
        ("用户C", "超级大傻逼")
    ]
    
    # 测试场景2：您的排练冲突例子
    scenario2 = [
        ("Ruochen Mao", "我们今天排练第三次了，你能不能这次按PPT内容来讲？"),
        ("小明", "昨天老师点名我们超时了……"),
        ("Ruochen Mao", "但那是因为你讲太久，我临场讲两句就顺带收尾了。"),
        ("小明", "我觉得讲稿念出来太死板了。")
    ]
    
    # 测试场景3：正常对话
    scenario3 = [
        ("张三", "今天天气不错"),
        ("李四", "是的，我们去公园吧"),
        ("张三", "好主意")
    ]
    
    scenarios = [
        ("攻击性语言测试", scenario1),
        ("排练冲突测试", scenario2),
        ("正常对话测试", scenario3)
    ]
    
    for scenario_name, conversation in scenarios:
        print(f"\n{'='*70}")
        print(f"🎭 {scenario_name}")
        print(f"{'='*70}")
        
        # 重置分析器
        analyzer = GPT4ConflictAnalyzer()
        
        for speaker, message in conversation:
            print(f"\n💬 {speaker}: {message}")
            
            start_time = asyncio.get_event_loop().time()
            result = await analyzer.analyze_conversation(speaker, message)
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 显示结果
            timestamp = datetime.now().strftime('%H:%M:%S')
            status = "🚨" if result.should_intervene else "✅"
            score_bar = format_score_bar(result.conflict_score)
            color_indicator = get_color_indicator(result.conflict_score)
            
            print(f"""
{status} [{timestamp}] 轮次#{len(analyzer.conversation_history)}
📊 冲突分数: {result.conflict_score:.2f} {score_bar} {color_indicator}
🔍 冲突类型: {result.conflict_type}
😊 情绪色调: {result.emotional_tone}
📈 升级风险: {result.escalation_risk:.2f}
🎯 推荐策略: {result.recommended_strategy.value}
⏱️  处理时间: {processing_time:.1f}ms
💭 GPT-4分析: {result.analysis_reasoning}
            """.strip())
            
            if result.should_intervene:
                print(f"🤖 智能干预: {result.intervention_message}")
            
            print("-" * 50)

async def interactive_llm_test():
    """交互式LLM测试"""
    print("\n🧪 GPT-4交互式冲突检测测试")
    print("=" * 50)
    print("输入对话来测试GPT-4响应（输入'quit'退出）")
    print("格式: 姓名: 消息内容")
    print()
    
    analyzer = GPT4ConflictAnalyzer()
    
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
            
            print("🤔 GPT-4正在分析...")
            
            start_time = asyncio.get_event_loop().time()
            result = await analyzer.analyze_conversation(speaker, message)
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 显示结果
            timestamp = datetime.now().strftime('%H:%M:%S')
            status = "🚨" if result.should_intervene else "✅"
            score_bar = format_score_bar(result.conflict_score)
            color_indicator = get_color_indicator(result.conflict_score)
            
            print(f"""
{status} [{timestamp}] {speaker} (轮次#{len(analyzer.conversation_history)})
📊 冲突分数: {result.conflict_score:.2f} {score_bar} {color_indicator}
🔍 冲突类型: {result.conflict_type}
😊 情绪色调: {result.emotional_tone}
📈 升级风险: {result.escalation_risk:.2f}
🎯 推荐策略: {result.recommended_strategy.value}
⏱️  处理时间: {processing_time:.1f}ms
💭 GPT-4分析: {result.analysis_reasoning}
            """.strip())
            
            if result.should_intervene:
                print(f"🤖 智能干预: {result.intervention_message}")
            
            print("─" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 测试结束")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

async def main():
    """主测试函数"""
    print("🤖 GPT-4冲突检测系统测试")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 请先在.env文件中配置OPENAI_API_KEY")
        return
    
    while True:
        print("\n请选择测试模式:")
        print("1. 预设场景测试")
        print("2. 交互式测试")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == '1':
            await test_llm_scenarios()
        elif choice == '2':
            await interactive_llm_test()
        elif choice == '3':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请输入1-3")

if __name__ == "__main__":
    asyncio.run(main())