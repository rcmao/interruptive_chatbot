"""
真实世界场景测试
模拟实际使用环境
"""

import asyncio
import time
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class RealWorldScenario:
    """真实世界场景"""
    name: str
    description: str
    conversation: List[Dict]
    expected_interventions: List[int]
    expected_effectiveness: float

class RealWorldTester:
    """真实世界测试器"""
    
    def __init__(self):
        self.scenarios = self._create_real_world_scenarios()
    
    def _create_real_world_scenarios(self) -> List[RealWorldScenario]:
        """创建真实世界场景"""
        return [
            RealWorldScenario(
                name="团队项目讨论",
                description="真实的团队项目讨论场景",
                conversation=[
                    {"speaker": "项目经理", "message": "我们需要在月底前完成这个功能", "timestamp": 0},
                    {"speaker": "开发员A", "message": "这个时间太紧了，不可能完成", "timestamp": 5},
                    {"speaker": "项目经理", "message": "你们总是找借口，其他团队都能按时完成", "timestamp": 10},
                    {"speaker": "开发员B", "message": "你根本不了解技术难度", "timestamp": 15},
                    {"speaker": "开发员A", "message": "我受够了这种不切实际的要求", "timestamp": 20},
                ],
                expected_interventions=[3, 4, 5],
                expected_effectiveness=0.8
            ),
            
            RealWorldScenario(
                name="设计评审会议",
                description="设计评审中的冲突场景",
                conversation=[
                    {"speaker": "设计师", "message": "这个设计方案考虑了用户体验", "timestamp": 0},
                    {"speaker": "产品经理", "message": "我觉得这个设计太复杂了", "timestamp": 5},
                    {"speaker": "设计师", "message": "你总是这样，从不理解设计的重要性", "timestamp": 10},
                    {"speaker": "产品经理", "message": "你错了，用户需要的是简单易用", "timestamp": 15},
                    {"speaker": "设计师", "message": "你根本不懂设计！", "timestamp": 20},
                ],
                expected_interventions=[3, 4, 5],
                expected_effectiveness=0.9
            ),
            
            RealWorldScenario(
                name="正常团队协作",
                description="正常的团队协作场景",
                conversation=[
                    {"speaker": "成员A", "message": "今天的会议很有收获", "timestamp": 0},
                    {"speaker": "成员B", "message": "是的，我们明确了下一步计划", "timestamp": 5},
                    {"speaker": "成员C", "message": "我们可以开始实施新的策略", "timestamp": 10},
                    {"speaker": "成员A", "message": "好的，我来负责第一部分", "timestamp": 15},
                ],
                expected_interventions=[],
                expected_effectiveness=1.0
            )
        ]
    
    async def run_real_world_test(self) -> Dict:
        """运行真实世界测试"""
        print("�� 真实世界场景测试")
        print("=" * 60)
        
        results = []
        
        for scenario in self.scenarios:
            print(f"\n�� 场景: {scenario.name}")
            print(f"描述: {scenario.description}")
            print("-" * 40)
            
            result = await self._test_scenario(scenario)
            results.append(result)
            
            self._print_scenario_result(result)
        
        # 生成综合报告
        overall_report = self._generate_overall_report(results)
        self._print_overall_report(overall_report)
        
        return overall_report
    
    async def _test_scenario(self, scenario: RealWorldScenario) -> Dict:
        """测试单个真实世界场景"""
        interventions = []
        response_times = []
        
        # 模拟实时对话
        for i, message_data in enumerate(scenario.conversation):
            # 模拟消息处理
            start_time = time.time()
            
            # 这里可以集成实际的检测器
            should_intervene = self._simulate_detection(message_data["message"])
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if should_intervene:
                interventions.append({
                    "step": i + 1,
                    "speaker": message_data["speaker"],
                    "message": message_data["message"],
                    "response_time": response_time
                })
            
            print(f"  {message_data['speaker']}: {message_data['message']}")
            if should_intervene:
                print(f"    🤖 干预触发 (响应时间: {response_time:.3f}s)")
        
        # 计算效果
        effectiveness = self._calculate_effectiveness(scenario, interventions)
        
        return {
            "scenario_name": scenario.name,
            "interventions": interventions,
            "response_times": response_times,
            "effectiveness": effectiveness,
            "expected_effectiveness": scenario.expected_effectiveness
        }
    
    def _simulate_detection(self, message: str) -> bool:
        """模拟冲突检测"""
        # 这里可以集成实际的检测器
        conflict_keywords = ["总是", "从不", "你错了", "受够了", "荒谬", "愚蠢"]
        return any(keyword in message for keyword in conflict_keywords)
    
    def _calculate_effectiveness(self, scenario: RealWorldScenario, interventions: List[Dict]) -> float:
        """计算干预效果"""
        if not scenario.expected_interventions:
            # 期望无干预的场景
            return 1.0 if not interventions else 0.0
        
        # 计算干预的准确性
        expected_steps = set(scenario.expected_interventions)
        actual_steps = set(intervention["step"] for intervention in interventions)
        
        if not expected_steps:
            return 1.0 if not actual_steps else 0.0
        
        precision = len(expected_steps & actual_steps) / len(actual_steps) if actual_steps else 1.0
        recall = len(expected_steps & actual_steps) / len(expected_steps)
        
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return f1_score
    
    def _print_scenario_result(self, result: Dict):
        """打印场景结果"""
        print(f"\n📊 场景结果: {result['scenario_name']}")
        print(f"   效果: {result['effectiveness']:.2f} (期望: {result['expected_effectiveness']:.2f})")
        print(f"   干预次数: {len(result['interventions'])}")
        
        if result['response_times']:
            avg_response_time = sum(result['response_times']) / len(result['response_times'])
            print(f"   平均响应时间: {avg_response_time:.3f}s")
    
    def _generate_overall_report(self, results: List[Dict]) -> Dict:
        """生成综合报告"""
        if not results:
            return {"error": "没有测试结果"}
        
        avg_effectiveness = sum(r['effectiveness'] for r in results) / len(results)
        total_interventions = sum(len(r['interventions']) for r in results)
        
        return {
            "total_scenarios": len(results),
            "avg_effectiveness": avg_effectiveness,
            "total_interventions": total_interventions,
            "scenario_details": [{"name": r['scenario_name'], "effectiveness": r['effectiveness']} for r in results]
        }
    
    def _print_overall_report(self, report: Dict):
        """打印综合报告"""
        print("\n" + "=" * 60)
        print("�� 真实世界测试报告")
        print("=" * 60)
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print(f"总测试场景: {report['total_scenarios']}")
        print(f"平均效果: {report['avg_effectiveness']:.2f}")
        print(f"总干预次数: {report['total_interventions']}")
        
        print("\n场景详情:")
        for detail in report['scenario_details']:
            status = "✅" if detail['effectiveness'] >= 0.8 else "⚠️" if detail['effectiveness'] >= 0.6 else "❌"
            print(f"  {status} {detail['name']}: {detail['effectiveness']:.2f}")

async def main():
    """主函数"""
    tester = RealWorldTester()
    results = await tester.run_real_world_test()
    return results

if __name__ == "__main__":
    asyncio.run(main()) 