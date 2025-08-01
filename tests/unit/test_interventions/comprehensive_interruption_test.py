"""
综合打断功能测试框架
测试chatbot打断的合理性、及时性和有效性
"""

import asyncio
import time
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入必要的模块
try:
    from src.detectors.optimized_monitor import OptimizedConflictMonitor
    from src.core.main import MessageData
    from src.interventions.intervention_generator import TKIStrategy, ConflictPhase
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保项目路径正确设置")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    messages: List[Dict]  # 消息序列
    expected_interventions: List[int]  # 期望干预的步骤
    expected_timing: List[float]  # 期望的响应时间
    expected_strategy: str  # 期望的TKI策略

@dataclass
class TestResult:
    """测试结果"""
    scenario_name: str
    interventions_triggered: List[Dict]
    response_times: List[float]
    accuracy: float
    timing_accuracy: float
    strategy_accuracy: float
    overall_score: float

class ComprehensiveInterruptionTester:
    """综合打断功能测试器"""
    
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
        self.test_scenarios = self._create_test_scenarios()
        
    def _create_test_scenarios(self) -> List[TestScenario]:
        """创建测试场景"""
        return [
            # 场景1: 渐进式冲突升级
            TestScenario(
                name="渐进式冲突升级",
                description="从轻微分歧到激烈冲突的完整过程",
                messages=[
                    {"role": "user1", "content": "我觉得这个方案还可以", "expected_intervention": False},
                    {"role": "user2", "content": "我有些不同意见", "expected_intervention": False},
                    {"role": "user1", "content": "为什么？有什么问题？", "expected_intervention": False},
                    {"role": "user2", "content": "这个设计考虑不周全", "expected_intervention": False},
                    {"role": "user1", "content": "你总是这样挑毛病", "expected_intervention": True},
                    {"role": "user2", "content": "你从不认真考虑别人的想法", "expected_intervention": True},
                    {"role": "user1", "content": "你错了，这样绝对不行！", "expected_intervention": True},
                ],
                expected_interventions=[5, 6, 7],  # 第5、6、7步应该干预
                expected_timing=[2.0, 1.5, 1.0],  # 响应时间应该越来越快
                expected_strategy="collaborating"
            ),
            
            # 场景2: 突发性激烈冲突
            TestScenario(
                name="突发性激烈冲突",
                description="突然出现的激烈冲突，需要快速干预",
                messages=[
                    {"role": "user1", "content": "今天天气不错", "expected_intervention": False},
                    {"role": "user2", "content": "我受够了你的无理取闹！", "expected_intervention": True},
                    {"role": "user1", "content": "你才是什么都不懂！", "expected_intervention": True},
                ],
                expected_interventions=[2, 3],
                expected_timing=[1.0, 0.8],  # 快速响应
                expected_strategy="accommodating"
            ),
            
            # 场景3: 发言权争夺
            TestScenario(
                name="发言权争夺",
                description="多人讨论中的发言权问题",
                messages=[
                    {"role": "user1", "content": "我认为我们应该...", "expected_intervention": False},
                    {"role": "user1", "content": "而且还有一点...", "expected_intervention": False},
                    {"role": "user1", "content": "另外...", "expected_intervention": False},
                    {"role": "user2", "content": "等等，让我说话...", "expected_intervention": True},
                    {"role": "user1", "content": "还有一个重要的点...", "expected_intervention": True},
                ],
                expected_interventions=[4, 5],
                expected_timing=[1.5, 1.0],
                expected_strategy="compromising"
            ),
            
            # 场景4: 情绪化表达
            TestScenario(
                name="情绪化表达",
                description="检测微妙的情绪信号",
                messages=[
                    {"role": "user1", "content": "这个想法太荒谬了", "expected_intervention": True},
                    {"role": "user2", "content": "你凭什么这样说我", "expected_intervention": True},
                    {"role": "user1", "content": "我受够了你的借口", "expected_intervention": True},
                ],
                expected_interventions=[1, 2, 3],
                expected_timing=[1.2, 1.0, 0.8],
                expected_strategy="collaborating"
            ),
            
            # 场景5: 无冲突场景（控制组）
            TestScenario(
                name="无冲突场景",
                description="正常讨论，不应该触发干预",
                messages=[
                    {"role": "user1", "content": "今天天气不错", "expected_intervention": False},
                    {"role": "user2", "content": "是的，很适合出去走走", "expected_intervention": False},
                    {"role": "user1", "content": "我们可以讨论一下项目进展", "expected_intervention": False},
                    {"role": "user2", "content": "好的，我最近完成了第一部分", "expected_intervention": False},
                ],
                expected_interventions=[],
                expected_timing=[],
                expected_strategy="none"
            )
        ]
    
    async def run_comprehensive_test(self) -> Dict:
        """运行综合测试"""
        print("🧪 开始综合打断功能测试")
        print("=" * 60)
        
        results = []
        
        for scenario in self.test_scenarios:
            print(f"\n📋 测试场景: {scenario.name}")
            print(f"描述: {scenario.description}")
            
            result = await self._test_scenario(scenario)
            results.append(result)
            
            # 打印场景结果
            self._print_scenario_result(result)
        
        # 生成综合报告
        overall_report = self._generate_overall_report(results)
        self._print_overall_report(overall_report)
        
        return overall_report
    
    async def _test_scenario(self, scenario: TestScenario) -> TestResult:
        """测试单个场景"""
        interventions_triggered = []
        response_times = []
        
        try:
            # 初始化监控器
            monitor = OptimizedConflictMonitor(self.api_key, self.api_base)
            await monitor.initialize()
            
            for i, message_data in enumerate(scenario.messages):
                # 创建消息数据
                message = MessageData(
                    author_id=1 if message_data["role"] == "user1" else 2,
                    author_name=message_data["role"],
                    content=message_data["content"],
                    timestamp=datetime.now(),
                    typing_duration=2.0,
                    edits_count=0,
                    reactions=[]
                )
                
                # 记录开始时间
                start_time = time.time()
                
                # 处理消息
                should_intervene, score, reason, signals = await monitor.process_message(message)
                
                # 记录响应时间
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                # 检查是否应该干预
                expected_intervention = message_data["expected_intervention"]
                if should_intervene:
                    interventions_triggered.append({
                        "step": i + 1,
                        "content": message_data["content"],
                        "score": score,
                        "reason": reason,
                        "response_time": response_time
                    })
                
                # 验证干预决策
                if should_intervene != expected_intervention:
                    print(f"   ⚠️ 步骤{i+1}: 干预决策不匹配 (实际:{should_intervene}, 期望:{expected_intervention})")
                
                print(f"  步骤{i+1}: {message_data['content'][:20]}... -> 分数:{score:.2f}, 干预:{should_intervene}, 时间:{response_time:.2f}s")
            
        except Exception as e:
            print(f"❌ 测试场景失败: {e}")
            # 返回默认结果
            return TestResult(
                scenario_name=scenario.name,
                interventions_triggered=[],
                response_times=[],
                accuracy=0.0,
                timing_accuracy=0.0,
                strategy_accuracy=0.0,
                overall_score=0.0
            )
        
        # 计算准确性指标
        accuracy = self._calculate_accuracy(scenario, interventions_triggered)
        timing_accuracy = self._calculate_timing_accuracy(scenario, response_times)
        strategy_accuracy = self._calculate_strategy_accuracy(scenario, interventions_triggered)
        
        return TestResult(
            scenario_name=scenario.name,
            interventions_triggered=interventions_triggered,
            response_times=response_times,
            accuracy=accuracy,
            timing_accuracy=timing_accuracy,
            strategy_accuracy=strategy_accuracy,
            overall_score=(accuracy + timing_accuracy + strategy_accuracy) / 3
        )
    
    def _calculate_accuracy(self, scenario: TestScenario, interventions: List[Dict]) -> float:
        """计算干预准确性"""
        expected_steps = set(scenario.expected_interventions)
        actual_steps = set(intervention["step"] for intervention in interventions)
        
        # 计算精确率和召回率
        precision = len(expected_steps & actual_steps) / len(actual_steps) if actual_steps else 1.0
        recall = len(expected_steps & actual_steps) / len(expected_steps) if expected_steps else 1.0
        
        # F1分数
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return f1_score
    
    def _calculate_timing_accuracy(self, scenario: TestScenario, response_times: List[float]) -> float:
        """计算响应时间准确性"""
        if not scenario.expected_timing:
            return 1.0  # 无期望干预的场景
        
        # 计算响应时间是否在合理范围内
        timing_scores = []
        for i, expected_time in enumerate(scenario.expected_timing):
            if i < len(response_times):
                actual_time = response_times[i]
                # 允许30%的误差
                tolerance = expected_time * 0.3
                if abs(actual_time - expected_time) <= tolerance:
                    timing_scores.append(1.0)
                else:
                    timing_scores.append(0.0)
        
        return sum(timing_scores) / len(timing_scores) if timing_scores else 1.0
    
    def _calculate_strategy_accuracy(self, scenario: TestScenario, interventions: List[Dict]) -> float:
        """计算策略选择准确性"""
        if scenario.expected_strategy == "none":
            return 1.0
        
        # 这里可以扩展为检查实际选择的TKI策略
        # 目前返回默认值，需要根据实际策略选择逻辑调整
        return 0.8  # 默认值
    
    def _print_scenario_result(self, result: TestResult):
        """打印场景结果"""
        print(f"\n📊 场景结果: {result.scenario_name}")
        print(f"   准确性: {result.accuracy:.2f}")
        print(f"   时间准确性: {result.timing_accuracy:.2f}")
        print(f"   策略准确性: {result.strategy_accuracy:.2f}")
        print(f"   综合分数: {result.overall_score:.2f}")
        
        if result.interventions_triggered:
            print(f"   触发干预: {len(result.interventions_triggered)}次")
            for intervention in result.interventions_triggered:
                print(f"     - 步骤{intervention['step']}: {intervention['content'][:30]}... (分数:{intervention['score']:.2f})")
    
    def _generate_overall_report(self, results: List[TestResult]) -> Dict:
        """生成综合报告"""
        if not results:
            return {"error": "没有测试结果"}
        
        avg_accuracy = sum(r.accuracy for r in results) / len(results)
        avg_timing = sum(r.timing_accuracy for r in results) / len(results)
        avg_strategy = sum(r.strategy_accuracy for r in results) / len(results)
        avg_overall = sum(r.overall_score for r in results) / len(results)
        
        total_interventions = sum(len(r.interventions_triggered) for r in results)
        
        return {
            "total_scenarios": len(results),
            "avg_accuracy": avg_accuracy,
            "avg_timing_accuracy": avg_timing,
            "avg_strategy_accuracy": avg_strategy,
            "avg_overall_score": avg_overall,
            "total_interventions": total_interventions,
            "scenario_details": [{"name": r.scenario_name, "score": r.overall_score} for r in results]
        }
    
    def _print_overall_report(self, report: Dict):
        """打印综合报告"""
        print("\n" + "=" * 60)
        print("📊 综合测试报告")
        print("=" * 60)
        
        if "error" in report:
            print(f"❌ {report['error']}")
            return
        
        print(f"总测试场景: {report['total_scenarios']}")
        print(f"平均准确性: {report['avg_accuracy']:.2f}")
        print(f"平均时间准确性: {report['avg_timing_accuracy']:.2f}")
        print(f"平均策略准确性: {report['avg_strategy_accuracy']:.2f}")
        print(f"平均综合分数: {report['avg_overall_score']:.2f}")
        print(f"总干预次数: {report['total_interventions']}")
        
        print("\n场景详情:")
        for detail in report['scenario_details']:
            status = "✅" if detail['score'] >= 0.7 else "⚠️" if detail['score'] >= 0.5 else "❌"
            print(f"  {status} {detail['name']}: {detail['score']:.2f}")
    
    async def test_real_time_performance(self) -> Dict:
        """测试实时性能"""
        print("\n⚡ 实时性能测试")
        print("-" * 40)
        
        try:
            monitor = OptimizedConflictMonitor(self.api_key, self.api_base)
            await monitor.initialize()
            
            # 模拟高并发消息
            concurrent_messages = [
                "这个想法太荒谬了！",
                "你总是这样不负责任",
                "我受够了你的借口",
                "你错了，这样绝对不行",
                "你从不考虑别人的想法"
            ]
            
            start_time = time.time()
            
            # 并发处理
            tasks = []
            for i, content in enumerate(concurrent_messages):
                message = MessageData(
                    author_id=i % 2 + 1,
                    author_name=f"user{i % 2 + 1}",
                    content=content,
                    timestamp=datetime.now(),
                    typing_duration=1.0,
                    edits_count=0,
                    reactions=[]
                )
                task = monitor.process_message(message)
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 分析结果
            successful_results = [r for r in results if not isinstance(r, Exception)]
            intervention_count = sum(1 for r in successful_results if r[0])  # should_intervene
            
            performance_metrics = {
                "total_messages": len(concurrent_messages),
                "total_processing_time": total_time,
                "avg_response_time": total_time / len(concurrent_messages),
                "intervention_rate": intervention_count / len(concurrent_messages),
                "success_rate": len(successful_results) / len(concurrent_messages)
            }
            
            print(f"📊 性能指标:")
            print(f"   总消息数: {performance_metrics['total_messages']}")
            print(f"   总处理时间: {performance_metrics['total_processing_time']:.2f}s")
            print(f"   平均响应时间: {performance_metrics['avg_response_time']:.3f}s")
            print(f"   干预率: {performance_metrics['intervention_rate']:.1%}")
            print(f"   成功率: {performance_metrics['success_rate']:.1%}")
            
            return performance_metrics
            
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            return {"error": str(e)}
    
    async def test_context_awareness(self) -> Dict:
        """测试上下文感知能力"""
        print("\n🧠 上下文感知测试")
        print("-" * 40)
        
        try:
            monitor = OptimizedConflictMonitor(self.api_key, self.api_base)
            await monitor.initialize()
            
            # 测试上下文连续性
            context_scenarios = [
                # 场景1: 持续冲突
                [
                    ("user1", "这个方案有问题"),
                    ("user2", "什么问题？"),
                    ("user1", "设计不合理"),
                    ("user2", "你总是挑毛病"),
                    ("user1", "你错了，这样不行")
                ],
                # 场景2: 冲突后和解
                [
                    ("user1", "这个想法太荒谬了"),
                    ("user2", "你凭什么这样说我"),
                    ("user1", "我受够了你的借口"),
                    ("user2", "算了，我们冷静一下"),
                    ("user1", "你说得对，我们重新开始")
                ]
            ]
            
            context_results = []
            
            for scenario_idx, scenario in enumerate(context_scenarios):
                print(f"\n场景 {scenario_idx + 1}:")
                scenario_interventions = []
                
                for step, (author, content) in enumerate(scenario):
                    message = MessageData(
                        author_id=1 if author == "user1" else 2,
                        author_name=author,
                        content=content,
                        timestamp=datetime.now(),
                        typing_duration=2.0,
                        edits_count=0,
                        reactions=[]
                    )
                    
                    should_intervene, score, reason, signals = await monitor.process_message(message)
                    
                    if should_intervene:
                        scenario_interventions.append({
                            "step": step + 1,
                            "content": content,
                            "score": score,
                            "reason": reason
                        })
                    
                    print(f"  步骤{step+1}: {content} -> 分数:{score:.2f}, 干预:{should_intervene}")
                
                context_results.append({
                    "scenario": scenario_idx + 1,
                    "interventions": scenario_interventions,
                    "intervention_count": len(scenario_interventions)
                })
            
            return {"context_results": context_results}
            
        except Exception as e:
            print(f"❌ 上下文测试失败: {e}")
            return {"error": str(e)}

async def main():
    """主测试函数"""
    # 配置API - 使用你的实际API配置
    api_key = "sk-XGGe5y0ZvLcQVFp6XnRizs7q47gsVnAbZx0Xr2mfcVlbr99f"
    api_base = "https://api2.aigcbest.top/v1"
    
    # 创建测试器
    tester = ComprehensiveInterruptionTester(api_key, api_base)
    
    try:
        # 运行综合测试
        print("🚀 开始综合打断功能测试...")
        comprehensive_results = await tester.run_comprehensive_test()
        
        # 运行性能测试
        print("\n🚀 开始性能测试...")
        performance_results = await tester.test_real_time_performance()
        
        # 运行上下文测试
        print("\n🚀 开始上下文感知测试...")
        context_results = await tester.test_context_awareness()
        
        # 生成最终报告
        final_report = {
            "comprehensive_results": comprehensive_results,
            "performance_results": performance_results,
            "context_results": context_results,
            "overall_assessment": _generate_overall_assessment(comprehensive_results, performance_results)
        }
        
        print("\n🎉 所有测试完成！")
        return final_report
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return {"error": str(e)}

def _generate_overall_assessment(comprehensive_results, performance_results):
    """生成整体评估"""
    if "error" in comprehensive_results or "error" in performance_results:
        return "❌ 测试失败，无法生成评估"
    
    avg_accuracy = comprehensive_results.get("avg_accuracy", 0)
    avg_timing = comprehensive_results.get("avg_timing_accuracy", 0)
    avg_response_time = performance_results.get("avg_response_time", 999)
    
    if avg_accuracy >= 0.8 and avg_timing >= 0.8 and avg_response_time <= 2.0:
        return "✅ 系统表现优秀，可以投入生产使用"
    elif avg_accuracy >= 0.6 and avg_timing >= 0.6:
        return "⚠️ 系统基本可用，建议进一步优化"
    else:
        return "❌ 系统需要重大改进"

if __name__ == "__main__":
    asyncio.run(main()) 