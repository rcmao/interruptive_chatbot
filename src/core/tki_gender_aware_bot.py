"""
基于TKI模型的性别意识智能干预机器人
整合新的检测器和TKI干预生成器
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from detectors.gender_based_interruption_detector import (
    GenderBasedInterruptionDetector, InterruptionTrigger, InterruptionType
)
from detectors.when_to_interrupt import WhenToInterruptDetector, InterruptionDecision
from interventions.tki_gender_aware_intervention import (
    TKIGenderAwareInterventionGenerator, TKIStrategy
)

@dataclass
class ConversationMetrics:
    """对话指标"""
    total_messages: int
    female_messages: int
    male_messages: int
    interventions_count: int
    strategy_distribution: Dict[str, int]
    interruption_type_distribution: Dict[str, int]
    average_urgency: float

class TKIGenderAwareBot:
    """基于TKI模型的性别意识智能干预机器人"""
    
    def __init__(self):
        self.detector = GenderBasedInterruptionDetector()
        self.when_to_interrupt_detector = WhenToInterruptDetector()
        self.intervention_generator = TKIGenderAwareInterventionGenerator()
        self.conversation_metrics = ConversationMetrics(
            total_messages=0,
            female_messages=0,
            male_messages=0,
            interventions_count=0,
            strategy_distribution={},
            interruption_type_distribution={},
            average_urgency=0.0
        )
        self.intervention_history = []
        self.conversation_context = {
            "participants": [],
            "participant_genders": {},
            "female_participants": [],
            "male_participants": [],
            "current_topic": "",
            "conversation_start": datetime.now()
        }
    
    async def process_message(self, message: str, author: str, 
                            gender: str = None, metadata: Dict = None) -> Dict:
        """处理消息并决定是否需要干预"""
        
        # 更新对话上下文
        self._update_context(author, gender, metadata)
        
        # 使用新的"when to interrupt"检测器
        interruption_decision = self.when_to_interrupt_detector.analyze_message(
            message, author, gender or 'unknown'
        )
        
        # 同时使用原有的检测器作为补充
        triggers = self.detector.detect_interruption_triggers(message, author, gender)
        
        # 综合决策：如果新检测器认为需要干预，或者原有检测器有高紧急程度的触发
        should_intervene = interruption_decision.should_interrupt
        
        # 如果新检测器没有检测到，但原有检测器有高紧急程度的触发，也进行干预
        if not should_intervene and triggers:
            highest_urgency_trigger = max(triggers, key=lambda t: t.urgency_level)
            if highest_urgency_trigger.urgency_level >= 4:
                should_intervene = True
        
        intervention_result = None
        
        if should_intervene:
            # 选择TKI策略
            if interruption_decision.should_interrupt:
                # 使用新检测器的决策
                strategy = self._select_tki_strategy_by_trigger_type(interruption_decision.trigger_type)
            else:
                # 使用原有检测器的决策
                strategy = self._select_tki_strategy(triggers[0], self.conversation_context)
            
            # 生成干预消息
            intervention_message = self.intervention_generator.generate_intervention(
                strategy, InterruptionType.STRUCTURAL_MARGINALIZATION, self.conversation_context
            )
            
            # 记录干预历史
            self._record_intervention_by_decision(interruption_decision, strategy, intervention_message)
            
            intervention_result = {
                "strategy": strategy.value,
                "message": intervention_message,
                "prompt_template": self.intervention_generator.get_prompt_template(strategy),
                "reasoning": interruption_decision.reasoning,
                "confidence": interruption_decision.confidence
            }
        
        return {
            "should_intervene": should_intervene,
            "intervention": intervention_result,
            "interruption_decision": {
                "should_interrupt": interruption_decision.should_interrupt,
                "trigger_type": interruption_decision.trigger_type.value,
                "urgency_level": interruption_decision.urgency_level,
                "confidence": interruption_decision.confidence,
                "reasoning": interruption_decision.reasoning,
                "evidence": interruption_decision.evidence
            },
            "triggers": [self._serialize_trigger(t) for t in triggers],
            "context": self.conversation_context,
            "metrics": self._get_current_metrics()
        }
    
    def _update_context(self, author: str, gender: str = None, metadata: Dict = None):
        """更新对话上下文"""
        # 添加新参与者
        if author not in self.conversation_context["participants"]:
            self.conversation_context["participants"].append(author)
        
        # 更新性别信息
        if gender:
            self.conversation_context["participant_genders"][author] = gender
            
            # 更新性别分组
            if gender == "female" and author not in self.conversation_context["female_participants"]:
                self.conversation_context["female_participants"].append(author)
            elif gender == "male" and author not in self.conversation_context["male_participants"]:
                self.conversation_context["male_participants"].append(author)
        
        # 更新消息计数
        self.conversation_metrics.total_messages += 1
        if gender == "female":
            self.conversation_metrics.female_messages += 1
        elif gender == "male":
            self.conversation_metrics.male_messages += 1
        
        # 更新主题
        if metadata and "topic" in metadata:
            self.conversation_context["current_topic"] = metadata["topic"]
    
    def _should_intervene(self, triggers: List[InterruptionTrigger]) -> bool:
        """决定是否需要干预"""
        if not triggers:
            return False
        
        # 获取最高紧急程度的触发时机
        highest_urgency_trigger = max(triggers, key=lambda t: t.urgency_level)
        
        # 根据紧急程度决定是否干预
        if highest_urgency_trigger.urgency_level >= 5:
            return True
        elif highest_urgency_trigger.urgency_level >= 4:
            # 检查是否已经频繁干预
            recent_interventions = [i for i in self.intervention_history 
                                  if (datetime.now() - i["timestamp"]).seconds < 300]  # 5分钟内
            return len(recent_interventions) < 3
        elif highest_urgency_trigger.urgency_level >= 3:
            # 检查是否已经频繁干预
            recent_interventions = [i for i in self.intervention_history 
                                  if (datetime.now() - i["timestamp"]).seconds < 600]  # 10分钟内
            return len(recent_interventions) < 2
        else:
            return False
    
    def _select_tki_strategy(self, trigger: InterruptionTrigger, context: Dict) -> TKIStrategy:
        """选择TKI策略"""
        return self.intervention_generator.select_strategy(
            trigger.interruption_type, context, trigger.urgency_level
        )
    
    def _select_tki_strategy_by_trigger_type(self, trigger_type) -> TKIStrategy:
        """根据触发类型选择TKI策略"""
        # 根据不同的触发类型选择不同的策略
        strategy_mapping = {
            'gender_imbalance': TKIStrategy.COLLABORATING,
            'expression_difficulty': TKIStrategy.ACCOMMODATING,
            'conversation_dominance': TKIStrategy.COMPETING,
            'silence_after_female': TKIStrategy.COLLABORATING,
            'male_consecutive': TKIStrategy.COMPETING,
            'female_interrupted': TKIStrategy.COMPETING,
            'aggressive_context': TKIStrategy.COMPETING
        }
        
        return strategy_mapping.get(trigger_type.value, TKIStrategy.COLLABORATING)
    
    def _record_intervention(self, trigger: InterruptionTrigger, strategy: TKIStrategy, message: str):
        """记录干预历史"""
        intervention_record = {
            "trigger": self._serialize_trigger(trigger),
            "strategy": strategy.value,
            "message": message,
            "timestamp": datetime.now()
        }
        
        self.intervention_history.append(intervention_record)
        self.conversation_metrics.interventions_count += 1
        
        # 更新策略分布
        if strategy.value not in self.conversation_metrics.strategy_distribution:
            self.conversation_metrics.strategy_distribution[strategy.value] = 0
        self.conversation_metrics.strategy_distribution[strategy.value] += 1
        
        # 更新打断类型分布
        trigger_type = trigger.interruption_type.value
        if trigger_type not in self.conversation_metrics.interruption_type_distribution:
            self.conversation_metrics.interruption_type_distribution[trigger_type] = 0
        self.conversation_metrics.interruption_type_distribution[trigger_type] += 1
    
    def _record_intervention_by_decision(self, decision: InterruptionDecision, strategy: TKIStrategy, message: str):
        """根据决策记录干预历史"""
        intervention_record = {
            "trigger_type": decision.trigger_type.value,
            "strategy": strategy.value,
            "message": message,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
            "urgency_level": decision.urgency_level,
            "evidence": decision.evidence,
            "timestamp": datetime.now()
        }
        
        self.intervention_history.append(intervention_record)
        self.conversation_metrics.interventions_count += 1
        
        # 更新策略分布
        if strategy.value not in self.conversation_metrics.strategy_distribution:
            self.conversation_metrics.strategy_distribution[strategy.value] = 0
        self.conversation_metrics.strategy_distribution[strategy.value] += 1
        
        # 更新打断类型分布
        trigger_type = decision.trigger_type.value
        if trigger_type not in self.conversation_metrics.interruption_type_distribution:
            self.conversation_metrics.interruption_type_distribution[trigger_type] = 0
        self.conversation_metrics.interruption_type_distribution[trigger_type] += 1
    
    def _serialize_trigger(self, trigger: InterruptionTrigger) -> Dict:
        """序列化触发时机"""
        return {
            "interruption_type": trigger.interruption_type.value,
            "pattern": trigger.pattern.value if trigger.pattern else None,
            "confidence": trigger.confidence,
            "evidence": trigger.evidence,
            "urgency_level": trigger.urgency_level,
            "recommended_action": trigger.recommended_action,
            "timestamp": trigger.timestamp.strftime("%H:%M:%S")
        }
    
    def _get_current_metrics(self) -> Dict:
        """获取当前指标"""
        return {
            "total_messages": self.conversation_metrics.total_messages,
            "female_messages": self.conversation_metrics.female_messages,
            "male_messages": self.conversation_metrics.male_messages,
            "interventions_count": self.conversation_metrics.interventions_count,
            "strategy_distribution": self.conversation_metrics.strategy_distribution,
            "interruption_type_distribution": self.conversation_metrics.interruption_type_distribution,
            "average_urgency": self.conversation_metrics.average_urgency,
            "conversation_duration": (datetime.now() - self.conversation_context["conversation_start"]).seconds
        }
    
    async def get_detailed_analysis(self) -> Dict:
        """获取详细分析报告"""
        detection_summary = self.detector.get_detection_summary()
        strategy_comparison = self.intervention_generator.get_strategy_comparison()
        
        return {
            "detection_summary": detection_summary,
            "strategy_comparison": strategy_comparison,
            "conversation_metrics": self._get_current_metrics(),
            "intervention_history": self.intervention_history[-10:],  # 最近10次干预
            "context_analysis": {
                "participant_count": len(self.conversation_context["participants"]),
                "female_participant_count": len(self.conversation_context["female_participants"]),
                "male_participant_count": len(self.conversation_context["male_participants"]),
                "current_topic": self.conversation_context["current_topic"],
                "conversation_duration_minutes": (datetime.now() - self.conversation_context["conversation_start"]).seconds / 60
            }
        }
    
    async def reset_conversation(self):
        """重置对话状态"""
        self.conversation_metrics = ConversationMetrics(
            total_messages=0,
            female_messages=0,
            male_messages=0,
            interventions_count=0,
            strategy_distribution={},
            interruption_type_distribution={},
            average_urgency=0.0
        )
        self.intervention_history = []
        self.conversation_context = {
            "participants": [],
            "participant_genders": {},
            "female_participants": [],
            "male_participants": [],
            "current_topic": "",
            "conversation_start": datetime.now()
        }
        self.detector.conversation_history = []
        self.detector.interruption_triggers = []

# 使用示例和测试
async def demo_tki_gender_aware_bot():
    """演示TKI性别意识机器人的使用"""
    
    bot = TKIGenderAwareBot()
    
    # 模拟乒乓球群聊场景
    test_conversations = [
        # 场景1：男性主导对话
        ("男生A", "male", "我觉得马龙反手更稳定，王楚钦还是欠点节奏。"),
        ("男生B", "male", "同意，这个分析很到位！"),
        ("男生A", "male", "我们可以从技术角度来分析..."),
        ("女生A", "female", "我...呃...觉得可能..."),
        
        # 场景2：女性观点被忽视
        ("女生A", "female", "我觉得我们需要考虑观众反馈。"),
        ("男生A", "male", "让我们继续讨论技术实现。"),
        
        # 场景3：女性被打断
        ("女生A", "female", "我认为我们应该..."),
        ("男生A", "male", "你等会再说，我们先讨论这个。"),
        
        # 场景4：性别定型言论
        ("女生A", "female", "我觉得这个战术很有创意。"),
        ("男生A", "male", "你懂球？你不就看脸？"),
    ]
    
    print("�� TKI性别意识机器人演示")
    print("=" * 50)
    
    for i, (author, gender, message) in enumerate(test_conversations):
        print(f"\n📝 消息 {i+1}: {author}({gender}) 说: {message}")
        
        result = await bot.process_message(message, author, gender)
        
        if result["should_intervene"]:
            intervention = result["intervention"]
            print(f"🤖 AI干预 ({intervention['strategy']}): {intervention['message']}")
        else:
            print("✅ 无需干预")
    
    # 获取详细分析
    analysis = await bot.get_detailed_analysis()
    print(f"\n📊 对话分析:")
    print(f"总消息数: {analysis['conversation_metrics']['total_messages']}")
    print(f"女性消息: {analysis['conversation_metrics']['female_messages']}")
    print(f"男性消息: {analysis['conversation_metrics']['male_messages']}")
    print(f"干预次数: {analysis['conversation_metrics']['interventions_count']}")
    print(f"策略分布: {analysis['conversation_metrics']['strategy_distribution']}")

if __name__ == "__main__":
    asyncio.run(demo_tki_gender_aware_bot())