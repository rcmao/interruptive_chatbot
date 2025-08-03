#!/usr/bin/env python3
"""
测试Web应用中的触发机制
模拟实际的消息发送和chatbot插话
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.workflow_manager import WorkflowManager
from src.core.unified_mapping import UnifiedMapping
from datetime import datetime

class WebTriggerSimulator:
    """Web触发机制模拟器"""
    
    def __init__(self):
        self.workflow = WorkflowManager()
        self.mapping = UnifiedMapping()
        self.room_id = 1
        self.users = {
            'alex': {'id': 1, 'name': 'Alex', 'gender': 'male'},
            'lily': {'id': 2, 'name': 'Lily', 'gender': 'female'},
            'zack': {'id': 3, 'name': 'Zack', 'gender': 'male'}
        }
        self.message_history = []
    
    async def simulate_message(self, username: str, content: str):
        """模拟发送消息"""
        user = self.users.get(username.lower())
        if not user:
            print(f"❌ 用户 {username} 不存在")
            return
        
        print(f"\n💬 {user['name']}({user['gender']}): {content}")
        
        # 记录消息
        message_data = {
            'id': len(self.message_history) + 1,
            'content': content,
            'author': user['name'],
            'gender': user['gender'],
            'timestamp': datetime.now(),
            'room_id': self.room_id,
            'user_id': user['id']
        }
        self.message_history.append(message_data)
        
        # 使用工作流处理消息
        result = await self.workflow.process_message(
            content, 
            user['name'], 
            user['gender']
        )
        
        if result.should_intervene:
            print(f"\n🤖 Chatbot插话!")
            print(f"   触发类型: {result.trigger_type} ({self.mapping.get_trigger_emoji(result.trigger_type)})")
            print(f"   策略: {result.strategy}")
            print(f"   插话内容: {result.suggested_intervention}")
            print(f"   置信度: {result.confidence:.2f}")
            print(f"   推理: {result.reasoning}")
            
            # 记录干预
            intervention_data = {
                'id': len(self.message_history) + 1,
                'content': result.suggested_intervention,
                'author': 'Chatbot',
                'gender': 'bot',
                'timestamp': datetime.now(),
                'room_id': self.room_id,
                'strategy': result.strategy,
                'trigger_type': result.trigger_type
            }
            self.message_history.append(intervention_data)
            
            return True
        else:
            print(f"   ❌ 未触发插话: {result.reasoning}")
            return False
    
    async def simulate_conversation_scenario(self, scenario_name: str, messages: list):
        """模拟完整的对话场景"""
        print(f"\n🎭 模拟场景: {scenario_name}")
        print("=" * 50)
        
        interventions_count = 0
        
        for username, content in messages:
            triggered = await self.simulate_message(username, content)
            if triggered:
                interventions_count += 1
        
        print(f"\n📊 场景总结:")
        print(f"   总消息数: {len(messages)}")
        print(f"   干预次数: {interventions_count}")
        print(f"   干预率: {interventions_count/len(messages)*100:.1f}%")
        
        return interventions_count
    
    def show_message_history(self):
        """显示消息历史"""
        print(f"\n📋 消息历史 (房间 {self.room_id}):")
        print("-" * 40)
        
        for i, msg in enumerate(self.message_history, 1):
            if msg['author'] == 'Chatbot':
                print(f"{i}. 🤖 {msg['author']}: {msg['content']}")
                print(f"   策略: {msg['strategy']}, 触发: {msg['trigger_type']}")
            else:
                print(f"{i}. {msg['author']}({msg['gender']}): {msg['content']}")
    
    def get_statistics(self):
        """获取统计信息"""
        total_messages = len(self.message_history)
        bot_messages = sum(1 for msg in self.message_history if msg['author'] == 'Chatbot')
        human_messages = total_messages - bot_messages
        
        male_messages = sum(1 for msg in self.message_history 
                           if msg['author'] != 'Chatbot' and msg['gender'] == 'male')
        female_messages = sum(1 for msg in self.message_history 
                             if msg['author'] != 'Chatbot' and msg['gender'] == 'female')
        
        return {
            'total_messages': total_messages,
            'human_messages': human_messages,
            'bot_messages': bot_messages,
            'male_messages': male_messages,
            'female_messages': female_messages,
            'intervention_rate': bot_messages / human_messages if human_messages > 0 else 0
        }

async def main():
    """主函数"""
    print("🤖 Web应用触发机制模拟测试")
    print("=" * 60)
    
    simulator = WebTriggerSimulator()
    
    # 场景1：女性被打断
    scenario1 = [
        ("alex", "马龙的反手太稳定了，王楚钦还差点"),
        ("zack", "就是，我觉得王楚钦还是不稳"),
        ("lily", "我觉得王楚钦的反击..."),
        ("alex", "不对，应该是这样"),
    ]
    
    await simulator.simulate_conversation_scenario("女性被打断", scenario1)
    
    # 场景2：女性被忽视
    scenario2 = [
        ("alex", "这个战术很有效"),
        ("lily", "我觉得我们可以考虑观众反馈"),
        ("zack", "继续讨论技术实现"),
        ("alex", "从技术角度分析..."),
    ]
    
    await simulator.simulate_conversation_scenario("女性被忽视", scenario2)
    
    # 场景3：男性主导对话
    scenario3 = [
        ("alex", "这个分析很准确"),
        ("zack", "完全同意"),
        ("alex", "从技术角度分析..."),
        ("zack", "我们应该深入讨论"),
    ]
    
    await simulator.simulate_conversation_scenario("男性主导对话", scenario3)
    
    # 场景4：攻击性语境
    scenario4 = [
        ("lily", "这个想法很有创意"),
        ("alex", "你懂什么？你只是看脸"),
    ]
    
    await simulator.simulate_conversation_scenario("攻击性语境", scenario4)
    
    # 显示消息历史
    simulator.show_message_history()
    
    # 显示统计信息
    stats = simulator.get_statistics()
    print(f"\n📊 总体统计:")
    print(f"   总消息数: {stats['total_messages']}")
    print(f"   人类消息: {stats['human_messages']}")
    print(f"   机器人消息: {stats['bot_messages']}")
    print(f"   男性消息: {stats['male_messages']}")
    print(f"   女性消息: {stats['female_messages']}")
    print(f"   干预率: {stats['intervention_rate']*100:.1f}%")
    
    print("\n🎉 Web触发机制测试完成！")

if __name__ == '__main__':
    asyncio.run(main()) 