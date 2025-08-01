"""
团队协作冲突场景专门测试脚本
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict

# 导入我们的系统组件
from thomas_conflict_model import EnhancedConflictMonitor
from scenario_specific_detector import TeamCollaborationConflictDetector
from real_time_optimization import UltraFastConflictDetector

class TeamCollaborationTester:
    """团队协作场景测试器"""
    
    def __init__(self):
        self.enhanced_monitor = EnhancedConflictMonitor()
        self.scenario_detector = TeamCollaborationConflictDetector()
        self.fast_detector = UltraFastConflictDetector()
        
        # 测试场景数据
        self.test_scenarios = {
            "leader_initial_concern": [
                "小李，我们明天就要presentation了，但是你负责的PPT部分还没有提交",
                "你已经连续两次没有参加小组会议了，我很担心我们的进度",
                "我感到有些不满，作为组长我需要确保项目按时完成"
            ],
            
            "member_defense": [
                "不好意思，最近课程压力真的很大，我不是故意的",
                "我觉得你可能没有理解我的处境，我已经尽力了",
                "我不希望被批评，我认为自己并没有做错什么"
            ],
            
            "escalation": [
                "你总是这样！为什么你从来不能按时完成任务？",
                "我受够了你的借口！这已经不是第一次了！",
                "你这样不负责任，我们整个小组都会受影响！"
            ],
            
            "high_conflict": [
                "你就是个不可靠的人！我再也不想和你合作了！",
                "你的态度让我非常愤怒！这完全不可接受！",
                "我要向老师反映你的问题，你这样的行为太过分了！"
            ]
        }
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 开始团队协作冲突检测系统测试")
        print("=" * 60)
        
        # 测试1: 基础检测功能
        await self.test_basic_detection()
        
        # 测试2: 实时性能测试
        await self.test_real_time_performance()
        
        # 测试3: Thomas模型阶段识别
        await self.test_thomas_stage_recognition()
        
        # 测试4: 干预策略选择
        await self.test_intervention_selection()
        
        # 测试5: 场景特化检测
        await self.test_scenario_specific_detection()
        
        print("\n🎉 所有测试完成！")
    
    async def test_basic_detection(self):
        """测试基础检测功能"""
        print("\n📋 测试1: 基础冲突检测功能")
        print("-" * 40)
        
        test_cases = [
            ("今天天气不错", "无冲突", 0.0),
            ("我觉得有些不满", "轻微冲突", 0.3),
            ("你总是这样不负责任", "中等冲突", 0.6),
            ("我受够了你的借口！", "高冲突", 0.8)
        ]
        
        for message, expected_level, expected_min_score in test_cases:
            # 使用快速检测器
            result = await self.fast_detector.ultra_fast_detect(message, "leader")
            
            success = "✅" if result["score"] >= expected_min_score else "❌"
            print(f"{success} '{message}' -> {result['score']:.2f} ({expected_level})")
            print(f"   原因: {', '.join(result['reasons'])}")
            print(f"   处理时间: {result['processing_time']:.1f}ms")
            print()
    
    async def test_real_time_performance(self):
        """测试实时性能"""
        print("⚡ 测试2: 实时性能测试")
        print("-" * 40)
        
        # 准备测试消息
        test_messages = []
        for scenario_messages in self.test_scenarios.values():
            test_messages.extend(scenario_messages)
        
        total_time = 0
        response_times = []
        
        for i, message in enumerate(test_messages):
            start_time = time.time()
            
            # 模拟完整的检测流程
            result = await self.fast_detector.ultra_fast_detect(message, "leader")
            
            processing_time = (time.time() - start_time) * 1000
            total_time += processing_time
            response_times.append(processing_time)
            
            print(f"消息 {i+1}: {processing_time:.1f}ms - {'干预' if result['should_intervene'] else '无需干预'}")
        
        avg_time = total_time / len(test_messages)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n📊 性能统计:")
        print(f"   平均响应时间: {avg_time:.1f}ms")
        print(f"   最快响应时间: {min_time:.1f}ms")
        print(f"   最慢响应时间: {max_time:.1f}ms")
        print(f"   目标达成: {'✅' if avg_time < 300 else '❌'} (<300ms)")
    
    async def test_thomas_stage_recognition(self):
        """测试Thomas阶段识别"""
        print("\n🧩 测试3: Thomas冲突阶段识别")
        print("-" * 40)
        
        stage_test_cases = [
            ("我感到很挫折，这个项目遇到了阻碍", "frustration"),
            ("我认为问题在于我们的沟通方式", "conceptualization"),
            ("我决定要重新安排任务分工", "behavior"),
            ("你刚才说的话让我很不舒服", "interaction"),
            ("如果这样下去，我们的项目肯定会失败", "outcomes")
        ]
        
        for message, expected_stage in stage_test_cases:
            # 使用场景特定检测器
            context = {"channel_id": "test", "author": "test_user"}
            signals = self.scenario_detector.detect_scenario_specific_conflict(
                message, "leader", context
            )
            
            detected_stage = signals.get("thomas_stage", {}).get("stage", "unknown")
            success = "✅" if expected_stage in str(detected_stage).lower() else "❌"
            
            print(f"{success} '{message}'")
            print(f"   期望阶段: {expected_stage}")
            print(f"   检测阶段: {detected_stage}")
            print()
    
    async def test_intervention_selection(self):
        """测试干预策略选择"""
        print("💡 测试4: 干预策略选择")
        print("-" * 40)
        
        from scenario_intervention import TeamCollaborationInterventions
        intervention_generator = TeamCollaborationInterventions()
        
        test_scenarios = [
            {
                "signals": {"leader_frustration": 0.6, "score": 0.5},
                "expected_type": "leader_frustration"
            },
            {
                "signals": {"member_defense": 0.5, "score": 0.4},
                "expected_type": "member_defense" 
            },
            {
                "signals": {"score": 0.8},
                "expected_type": "escalation_prevention"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios):
            intervention = intervention_generator.select_intervention(
                scenario["signals"], 
                {"turn": i}
            )
            
            print(f"场景 {i+1}: {scenario['expected_type']}")
            print(f"   干预消息: {intervention}")
            print(f"   消息长度: {len(intervention)} 字符")
            print()
    
    async def test_scenario_specific_detection(self):
        """测试场景特化检测"""
        print("🎯 测试5: 场景特化检测")
        print("-" * 40)
        
        role_specific_tests = [
            {
                "role": "leader",
                "messages": self.test_scenarios["leader_initial_concern"],
                "expected_signal": "leader_frustration"
            },
            {
                "role": "member", 
                "messages": self.test_scenarios["member_defense"],
                "expected_signal": "member_defense"
            }
        ]
        
        for test_case in role_specific_tests:
            print(f"\n角色: {test_case['role']}")
            
            for message in test_case["messages"]:
                context = {"channel_id": "test", "turn": 1}
                signals = self.scenario_detector.detect_scenario_specific_conflict(
                    message, test_case["role"], context
                )
                
                signal_value = signals.get(test_case["expected_signal"], 0)
                success = "✅" if signal_value > 0.3 else "❌"
                
                print(f"  {success} '{message[:30]}...'")
                print(f"      {test_case['expected_signal']}: {signal_value:.2f}")

# 简化的场景模拟测试
class QuickScenarioTest:
    """快速场景模拟测试"""
    
    def __init__(self):
        self.conversation_log = []
        self.intervention_log = []
    
    async def simulate_conversation(self):
        """模拟完整对话场景"""
        print("\n🎭 模拟真实对话场景")
        print("=" * 50)
        
        # 模拟对话流程
        conversation_script = [
            {"role": "leader", "message": "小王，我们明天presentation，你的PPT部分准备好了吗？", "expected_intervention": False},
            {"role": "member", "message": "额...还没有完全准备好，不好意思", "expected_intervention": False},
            {"role": "leader", "message": "什么？你已经拖了一周了！我们小组要因为你搞砸了！", "expected_intervention": True},
            {"role": "member", "message": "我最近真的很忙，你不要这样说我", "expected_intervention": False},
            {"role": "leader", "message": "我受够了你的借口！你就是不负责任！", "expected_intervention": True},
            {"role": "member", "message": "你凭什么这样说我？我也很努力了！", "expected_intervention": True}
        ]
        
        detector = UltraFastConflictDetector()
        
        for turn, exchange in enumerate(conversation_script):
            print(f"\n回合 {turn + 1}:")
            print(f"【{exchange['role']}】: {exchange['message']}")
            
            # 检测冲突
            result = await detector.ultra_fast_detect(exchange['message'], exchange['role'])
            
            should_intervene = result['should_intervene']
            expected = exchange['expected_intervention']
            
            accuracy = "✅" if should_intervene == expected else "❌"
            print(f"   检测结果: {'需要干预' if should_intervene else '无需干预'} (期望: {'需要' if expected else '无需'})")
            print(f"   准确性: {accuracy}")
            print(f"   冲突分数: {result['score']:.2f}")
            print(f"   响应时间: {result['processing_time']:.1f}ms")
            
            if should_intervene:
                print(f"   🤖 干预: 我注意到对话有些紧张，让我们保持冷静...")

async def main():
    """主测试函数"""
    print("🧪 团队协作冲突干预系统 - 综合测试")
    print("=" * 60)
    
    # 运行基础测试
    tester = TeamCollaborationTester()
    await tester.run_comprehensive_test()
    
    # 运行场景模拟
    scenario_tester = QuickScenarioTest()
    await scenario_tester.simulate_conversation()
    
    print("\n📊 测试总结:")
    print("✅ 如果大部分测试通过，系统可以进入下一阶段测试")
    print("❌ 如果有测试失败，需要先修复相关问题")
    print("\n📋 下一步建议:")
    print("1. 在Discord中进行真实环境测试")
    print("2. 邀请同事进行角色扮演测试")
    print("3. 收集反馈并调整干预策略")

if __name__ == "__main__":
    asyncio.run(main()) 