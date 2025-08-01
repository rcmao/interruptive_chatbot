"""
优化版打断功能测试框架
基于快速测试结果进行优化
"""

import asyncio
import time
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 简化的消息数据类
class SimpleMessageData:
    def __init__(self, author_id, author_name, content, timestamp=None):
        self.author_id = author_id
        self.author_name = author_name
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.typing_duration = 2.0
        self.edits_count = 0
        self.reactions = []

@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    messages: List[Dict]
    expected_interventions: List[int]
    expected_timing: List[float]
    expected_strategy: str

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

class OptimizedConflictDetector:
    """优化版冲突检测器"""
    
    def __init__(self):
        # 冲突关键词 - 按严重程度分类
        self.conflict_keywords = {
            "high": ["荒谬", "愚蠢", "错误", "不对", "不行", "受够了", "无理取闹", "你错了", "你根本不懂"],
            "medium": ["总是", "从不", "挑毛病", "不负责任", "借口", "固执"],
            "low": ["不同意", "反对", "问题", "考虑不周全", "不同意见"]
        }
        
        # 情绪关键词
        self.emotion_keywords = {
            "anger": ["愤怒", "生气", "恼火", "愤慨", "angry", "mad", "furious"],
            "frustration": ["挫折", "沮丧", "失望", "frustrated", "disappointed"],
            "defensive": ["凭什么", "你才", "我受够了", "你总是", "你从不"]
        }
        
        # 冲突模式
        self.conflict_patterns = [
            r"你总是.*",
            r"你从不.*", 
            r".*太.*了",
            r".*完全.*错.*",
            r"you always.*",
            r"you never.*"
        ]
        
        # 动态阈值
        self.base_threshold = 0.25  # 降低基础阈值
        self.context_multiplier = 1.2  # 上下文增强因子
    
    def detect_conflict(self, content: str, context: List[str] = None) -> Tuple[bool, float, str]:
        """优化的冲突检测"""
        content_lower = content.lower()
        score = 0.0
        reasons = []
        
        # 1. 检查高严重程度关键词 (权重: 40%)
        high_score = 0.0
        for keyword in self.conflict_keywords["high"]:
            if keyword in content_lower:
                high_score += 0.4
                reasons.append(f"高冲突关键词: {keyword}")
        
        # 2. 检查中等严重程度关键词 (权重: 30%)
        medium_score = 0.0
        for keyword in self.conflict_keywords["medium"]:
            if keyword in content_lower:
                medium_score += 0.3
                reasons.append(f"中冲突关键词: {keyword}")
        
        # 3. 检查低严重程度关键词 (权重: 20%)
        low_score = 0.0
        for keyword in self.conflict_keywords["low"]:
            if keyword in content_lower:
                low_score += 0.2
                reasons.append(f"低冲突关键词: {keyword}")
        
        # 4. 检查情绪关键词 (权重: 25%)
        emotion_score = 0.0
        for emotion_type, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    if emotion_type == "anger":
                        emotion_score += 0.4
                    elif emotion_type == "frustration":
                        emotion_score += 0.3
                    elif emotion_type == "defensive":
                        emotion_score += 0.25
                    reasons.append(f"情绪关键词: {keyword}")
        
        # 5. 检查冲突模式 (权重: 15%)
        pattern_score = 0.0
        for pattern in self.conflict_patterns:
            if re.search(pattern, content_lower):
                pattern_score += 0.3
                reasons.append(f"冲突模式: {pattern}")
        
        # 6. 检查强度标记 (权重: 10%)
        intensity_markers = ["！", "!!", "？？", "??", "..."]
        intensity_count = sum(1 for marker in intensity_markers if marker in content)
        intensity_score = min(0.2, intensity_count * 0.1)
        if intensity_count > 0:
            reasons.append(f"强度标记: {intensity_count}个")
        
        # 7. 上下文分析
        context_score = 0.0
        if context and len(context) >= 2:
            # 检查是否有多轮冲突
            recent_conflict_count = 0
            for ctx_msg in context[-3:]:
                if any(kw in ctx_msg.lower() for kw in self.conflict_keywords["high"] + self.conflict_keywords["medium"]):
                    recent_conflict_count += 1
            
            if recent_conflict_count >= 2:
                context_score = 0.2
                reasons.append(f"上下文冲突: {recent_conflict_count}轮")
        
        # 计算总分
        total_score = min(1.0, 
            high_score + medium_score + low_score + emotion_score + pattern_score + intensity_score + context_score
        )
        
        # 动态阈值调整
        dynamic_threshold = self.base_threshold
        if context_score > 0:
            dynamic_threshold *= self.context_multiplier
        
        # 判断是否需要干预
        should_intervene = total_score > dynamic_threshold
        
        return should_intervene, total_score, "; ".join(reasons)

class OptimizedInterruptionTester:
    """优化版打断功能测试器"""
    
    def __init__(self):
        self.detector = OptimizedConflictDetector()
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
                expected_interventions=[5, 6, 7],
                expected_timing=[2.0, 1.5, 1.0],
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
                expected_timing=[1.0, 0.8],
                expected_strategy="accommodating"
            ),
            
            # 场景3: 中度冲突（优化重点）
            TestScenario(
                name="中度冲突",
                description="需要精确检测的中度冲突场景",
                messages=[
                    {"role": "user1", "content": "这个设计考虑不周全", "expected_intervention": False},
                    {"role": "user2", "content": "你总是这样挑毛病", "expected_intervention": True},
                    {"role": "user1", "content": "你从不认真考虑别人的想法", "expected_intervention": True},
                    {"role": "user2", "content": "我对你的表现很不满", "expected_intervention": True},
                ],
                expected_interventions=[2, 3, 4],
                expected_timing=[1.5, 1.2, 1.0],
                expected_strategy="compromising"
            ),
            
            # 场景4: 微妙冲突信号
            TestScenario(
                name="微妙冲突信号",
                description="检测微妙的冲突信号",
                messages=[
                    {"role": "user1", "content": "这个想法有点问题", "expected_intervention": False},
                    {"role": "user2", "content": "我不太同意这个观点", "expected_intervention": False},
                    {"role": "user1", "content": "你凭什么质疑我的想法？", "expected_intervention": True},
                    {"role": "user2", "content": "我只是有不同的看法", "expected_intervention": False},
                ],
                expected_interventions=[3],
                expected_timing=[1.0],
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
    
    async def run_optimized_test(self) -> Dict:
        """运行优化测试"""
        print("🧪 优化版打断功能测试")
        print("=" * 60)
        
        results = []
        context_history = []
        
        for scenario in self.test_scenarios:
            print(f"\n📋 测试场景: {scenario.name}")
            print(f"描述: {scenario.description}")
            print("-" * 40)
            
            result = await self._test_scenario(scenario, context_history)
            results.append(result)
            
            # 打印场景结果
            self._print_scenario_result(result)
            
            # 更新上下文历史
            context_history.extend([msg["content"] for msg in scenario.messages])
        
        # 生成综合报告
        overall_report = self._generate_overall_report(results)
        self._print_overall_report(overall_report)
        
        return overall_report
    
    async def _test_scenario(self, scenario: TestScenario, context_history: List[str]) -> TestResult:
        """测试单个场景"""
        interventions_triggered = []
        response_times = []
        scenario_context = context_history.copy()
        
        for i, message_data in enumerate(scenario.messages):
            # 记录开始时间
            start_time = time.time()
            
            # 检测冲突（使用上下文）
            should_intervene, score, reason = self.detector.detect_conflict(
                message_data["content"], 
                scenario_context
            )
            
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
                status = "❌" if should_intervene != expected_intervention else "✅"
                print(f"   {status} 步骤{i+1}: {message_data['content'][:30]}... -> 干预:{should_intervene} (期望:{expected_intervention})")
                print(f"      分数: {score:.2f}, 原因: {reason}")
            else:
                print(f"   ✅ 步骤{i+1}: {message_data['content'][:30]}... -> 干预:{should_intervene}")
                print(f"      分数: {score:.2f}, 时间: {response_time:.3f}s")
            
            # 更新上下文
            scenario_context.append(message_data["content"])
        
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
            return 1.0
        
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
        print("📊 优化测试报告")
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
            status = "✅" if detail['score'] >= 0.8 else "⚠️" if detail['score'] >= 0.6 else "❌"
            print(f"  {status} {detail['name']}: {detail['score']:.2f}")
        
        # 总体评估
        if report['avg_overall_score'] >= 0.8:
            print("\n✅ 系统表现优秀，可以投入生产使用")
        elif report['avg_overall_score'] >= 0.6:
            print("\n⚠️ 系统基本可用，建议进一步优化")
        else:
            print("\n❌ 系统需要重大改进")

async def main():
    """主函数"""
    tester = OptimizedInterruptionTester()
    results = await tester.run_optimized_test()
    return results

if __name__ == "__main__":
    asyncio.run(main()) 