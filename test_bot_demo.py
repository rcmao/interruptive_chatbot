#!/usr/bin/env python3
"""
TKI性别意识智能干预机器人演示脚本
"""

import asyncio
import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def demo_bot():
    """演示机器人功能"""
    try:
        from core.tki_gender_aware_bot import TKIGenderAwareBot
        
        print("🤖 启动TKI性别意识智能干预机器人...")
        bot = TKIGenderAwareBot()
        
        # 模拟对话场景
        print("\n📝 模拟对话场景：")
        print("=" * 50)
        
        # 场景1：男性主导对话
        print("\n场景1：男性主导对话")
        print("-" * 30)
        
        result1 = await bot.process_message(
            message="我认为这个方案是最好的，我们应该立即实施。",
            author="张三",
            gender="male"
        )
        print(f"用户: 我认为这个方案是最好的，我们应该立即实施。")
        print(f"性别: 男性")
        if result1.get("should_intervene"):
            print(f"🤖 AI干预: {result1['intervention']['message']}")
        else:
            print("✅ 无需干预")
        
        result2 = await bot.process_message(
            message="我...我觉得也许我们可以再考虑一下其他选项...",
            author="李四",
            gender="female"
        )
        print(f"\n用户: 我...我觉得也许我们可以再考虑一下其他选项...")
        print(f"性别: 女性")
        if result2.get("should_intervene"):
            print(f"🤖 AI干预: {result2['intervention']['message']}")
        else:
            print("✅ 无需干预")
        
        # 场景2：性别刻板印象
        print("\n\n场景2：性别刻板印象")
        print("-" * 30)
        
        result3 = await bot.process_message(
            message="你一个女孩子懂什么技术？",
            author="王五",
            gender="male"
        )
        print(f"用户: 你一个女孩子懂什么技术？")
        print(f"性别: 男性")
        if result3.get("should_intervene"):
            print(f"🤖 AI干预: {result3['intervention']['message']}")
        else:
            print("✅ 无需干预")
        
        # 获取详细分析
        print("\n\n📊 对话分析报告：")
        print("=" * 50)
        try:
            analysis = await bot.get_detailed_analysis()
            print(f"总消息数: {analysis.get('metrics', {}).get('total_messages', 0)}")
            print(f"女性消息数: {analysis.get('metrics', {}).get('female_messages', 0)}")
            print(f"男性消息数: {analysis.get('metrics', {}).get('male_messages', 0)}")
            print(f"干预次数: {analysis.get('metrics', {}).get('interventions_count', 0)}")
            print(f"平均紧急程度: {analysis.get('metrics', {}).get('average_urgency', 0.0):.2f}")
            
            print("\n🎯 TKI策略分布:")
            strategy_dist = analysis.get('metrics', {}).get('strategy_distribution', {})
            if strategy_dist:
                for strategy, count in strategy_dist.items():
                    print(f"  {strategy}: {count}次")
            else:
                print("  暂无策略使用记录")
        except Exception as e:
            print(f"获取分析报告时出错: {e}")
        
        print("\n✅ 演示完成！")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请确保所有依赖已安装")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    asyncio.run(demo_bot()) 