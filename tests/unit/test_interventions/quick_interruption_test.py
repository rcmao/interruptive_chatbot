"""
快速打断功能测试
用于快速验证chatbot打断功能
"""

import asyncio
import time
import sys
import os
from datetime import datetime

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

# 简化的冲突检测器
class SimpleConflictDetector:
    def __init__(self):
        self.conflict_keywords = [
            "荒谬", "愚蠢", "错误", "不对", "不行", "受够了", 
            "总是", "从不", "你错了", "你根本不懂", "无理取闹"
        ]
        self.emotion_keywords = [
            "愤怒", "生气", "恼火", "愤慨", "angry", "mad", "furious",
            "挫折", "沮丧", "失望", "frustrated", "disappointed"
        ]
    
    def detect_conflict(self, content: str) -> tuple[bool, float, str]:
        """简单的冲突检测"""
        content_lower = content.lower()
        score = 0.0
        reasons = []
        
        # 检查冲突关键词
        for keyword in self.conflict_keywords:
            if keyword in content_lower:
                score += 0.3
                reasons.append(f"检测到冲突关键词: {keyword}")
        
        # 检查情绪关键词
        for keyword in self.emotion_keywords:
            if keyword in content_lower:
                score += 0.2
                reasons.append(f"检测到情绪关键词: {keyword}")
        
        # 检查标点符号强度
        intensity_markers = ["！", "!!", "？？", "??"]
        intensity_count = sum(1 for marker in intensity_markers if marker in content)
        if intensity_count > 0:
            score += intensity_count * 0.1
            reasons.append(f"检测到强度标记: {intensity_count}个")
        
        # 限制分数在0-1之间
        score = min(1.0, score)
        
        # 判断是否需要干预
        should_intervene = score > 0.4
        
        return should_intervene, score, "; ".join(reasons)

class QuickInterruptionTester:
    """快速打断功能测试器"""
    
    def __init__(self):
        self.detector = SimpleConflictDetector()
        self.test_scenarios = self._create_test_scenarios()
    
    def _create_test_scenarios(self):
        """创建测试场景"""
        return [
            {
                "name": "轻度分歧",
                "messages": [
                    "我觉得这个方案还可以",
                    "我有些不同意见",
                    "为什么？有什么问题？"
                ],
                "expected_interventions": []
            },
            {
                "name": "中度冲突",
                "messages": [
                    "这个设计考虑不周全",
                    "你总是这样挑毛病",
                    "你从不认真考虑别人的想法"
                ],
                "expected_interventions": [2, 3]
            },
            {
                "name": "激烈冲突",
                "messages": [
                    "这个想法太荒谬了！",
                    "你错了，这样绝对不行！",
                    "我受够了你的无理取闹！"
                ],
                "expected_interventions": [1, 2, 3]
            },
            {
                "name": "正常讨论",
                "messages": [
                    "今天天气不错",
                    "是的，很适合出去走走",
                    "我们可以讨论一下项目进展"
                ],
                "expected_interventions": []
            }
        ]
    
    async def run_quick_test(self):
        """运行快速测试"""
        print("🧪 快速打断功能测试")
        print("=" * 50)
        
        results = []
        
        for scenario in self.test_scenarios:
            print(f"\n📋 测试场景: {scenario['name']}")
            print("-" * 30)
            
            scenario_results = []
            
            for i, message in enumerate(scenario['messages']):
                # 创建消息数据
                msg_data = SimpleMessageData(
                    author_id=i % 2 + 1,
                    author_name=f"user{i % 2 + 1}",
                    content=message
                )
                
                # 记录开始时间
                start_time = time.time()
                
                # 检测冲突
                should_intervene, score, reason = self.detector.detect_conflict(message)
                
                # 记录响应时间
                response_time = time.time() - start_time
                
                # 检查是否应该干预
                expected_intervention = (i + 1) in scenario['expected_interventions']
                
                # 记录结果
                result = {
                    "step": i + 1,
                    "content": message,
                    "should_intervene": should_intervene,
                    "expected_intervention": expected_intervention,
                    "score": score,
                    "reason": reason,
                    "response_time": response_time,
                    "correct": should_intervene == expected_intervention
                }
                
                scenario_results.append(result)
                
                # 打印结果
                status = "✅" if result['correct'] else "❌"
                intervention_status = "干预" if should_intervene else "不干预"
                print(f"  {status} 步骤{i+1}: {message[:30]}... -> {intervention_status} (分数:{score:.2f}, 时间:{response_time:.3f}s)")
                if reason:
                    print(f"     原因: {reason}")
            
            # 计算场景准确性
            correct_count = sum(1 for r in scenario_results if r['correct'])
            accuracy = correct_count / len(scenario_results)
            
            results.append({
                "scenario_name": scenario['name'],
                "accuracy": accuracy,
                "results": scenario_results
            })
            
            print(f"  场景准确性: {accuracy:.2f} ({correct_count}/{len(scenario_results)})")
        
        # 生成总体报告
        self._print_overall_report(results)
        
        return results
    
    def _print_overall_report(self, results):
        """打印总体报告"""
        print("\n" + "=" * 50)
        print("📊 测试总结")
        print("=" * 50)
        
        total_scenarios = len(results)
        avg_accuracy = sum(r['accuracy'] for r in results) / total_scenarios
        total_interventions = sum(len([r for r in scenario['results'] if r['should_intervene']]) for scenario in results)
        
        print(f"总测试场景: {total_scenarios}")
        print(f"平均准确性: {avg_accuracy:.2f}")
        print(f"总干预次数: {total_interventions}")
        
        print("\n场景详情:")
        for result in results:
            status = "✅" if result['accuracy'] >= 0.8 else "⚠️" if result['accuracy'] >= 0.6 else "❌"
            print(f"  {status} {result['scenario_name']}: {result['accuracy']:.2f}")
        
        # 总体评估
        if avg_accuracy >= 0.8:
            print("\n🎉 系统表现良好，可以进一步测试")
        elif avg_accuracy >= 0.6:
            print("\n⚠️ 系统基本可用，需要优化")
        else:
            print("\n❌ 系统需要重大改进")

async def main():
    """主函数"""
    tester = QuickInterruptionTester()
    results = await tester.run_quick_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())