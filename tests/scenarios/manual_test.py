"""
手动测试场景脚本
用于在Discord环境中手动测试系统功能
"""

import asyncio
from datetime import datetime
from main import RealTimeInteractionModule

class ManualTestSuite:
    """手动测试套件"""
    
    def __init__(self, api_key: str, api_base: str):
        self.interaction_module = RealTimeInteractionModule(api_key, api_base)
        self.test_scenarios = self._create_test_scenarios()
    
    def _create_test_scenarios(self):
        """创建测试场景"""
        return {
            "scenario_1": {
                "name": "轻度技术分歧",
                "description": "关于技术选型的正常讨论",
                "messages": [
                    "我觉得我们应该用React来开发前端",
                    "Vue.js可能更适合我们的团队",
                    "React的生态系统确实更成熟一些",
                    "但是Vue的学习曲线更平缓"
                ],
                "expected": "无干预或轻度协作干预"
            },
            
            "scenario_2": {
                "name": "观点冲突升级",
                "description": "从分歧到情绪化表达",
                "messages": [
                    "这个设计方案有问题",
                    "我不觉得有什么问题，很合理啊",
                    "你从不认真考虑用户体验",
                    "你错了，我一直很关注用户体验",
                    "你总是这样固执己见"
                ],
                "expected": "中度干预，竞争或协作策略"
            },
            
            "scenario_3": {
                "name": "激烈争论",
                "description": "高强度冲突场景",
                "messages": [
                    "这个想法完全荒谬！",
                    "你根本不懂这个领域，别胡说八道",
                    "你才是什么都不懂的人！",
                    "我受够了你的无理取闹",
                    "那你就别参与这个项目了"
                ],
                "expected": "立即干预，竞争策略"
            },
            
            "scenario_4": {
                "name": "发言权不平衡",
                "description": "一方过度主导讨论",
                "messages": [
                    "我认为我们应该这样做：首先...",
                    "然后我们需要考虑...",
                    "另外还有一个重要的点...",
                    "等等，让我也说几句...",
                    "最后，我想强调的是..."
                ],
                "expected": "包容策略干预"
            }
        }
    
    def print_scenario_instructions(self):
        """打印测试说明"""
        print("🎯 手动测试场景指南")
        print("=" * 50)
        print("在Discord频道中按顺序发送以下消息，观察机器人响应：\n")
        
        for scenario_id, scenario in self.test_scenarios.items():
            print(f"【{scenario['name']}】")
            print(f"描述: {scenario['description']}")
            print(f"预期结果: {scenario['expected']}")
            print("测试消息:")
            
            for i, message in enumerate(scenario["messages"], 1):
                print(f"  {i}. {message}")
            
            print(f"{'='*50}\n")
    
    def generate_test_checklist(self):
        """生成测试检查清单"""
        checklist = """
🔍 测试检查清单

## 功能测试
- [ ] 消息监听正常工作
- [ ] 冲突分数计算准确
- [ ] 情绪化表达检测有效
- [ ] 发言权问题识别正确
- [ ] 打字行为分析工作
- [ ] TKI策略选择合理
- [ ] 干预消息生成自然
- [ ] 冷却机制防止过度干预

## 性能测试
- [ ] 响应时间 < 200ms
- [ ] 并发处理能力正常
- [ ] 内存使用合理
- [ ] API调用频率适中

## 边界测试
- [ ] 空消息处理
- [ ] 特殊字符处理
- [ ] 长消息处理
- [ ] 快速连续消息
- [ ] 网络异常处理
- [ ] API失败降级

## 用户体验测试
- [ ] 干预时机合适
- [ ] 干预消息友好
- [ ] 不影响正常讨论
- [ ] 用户接受度高

## 部署前最终检查
- [ ] 所有单元测试通过
- [ ] 集成测试通过
- [ ] 性能满足要求
- [ ] 错误处理完善
- [ ] 日志记录完整
- [ ] 配置文件正确
        """
        
        with open("test_checklist.md", "w", encoding="utf-8") as f:
            f.write(checklist)
        
        print("✅ 测试检查清单已生成: test_checklist.md")

if __name__ == "__main__":
    # 创建测试套件
    test_suite = ManualTestSuite("your_api_key", "your_api_base")
    
    # 打印测试说明
    test_suite.print_scenario_instructions()
    
    # 生成检查清单
    test_suite.generate_test_checklist()
    
    print("📖 手动测试准备就绪！")
    print("1. 启动机器人: python main.py")
    print("2. 在Discord频道中执行测试场景")
    print("3. 使用检查清单验证功能") 