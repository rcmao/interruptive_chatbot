"""
基于TKI模型的干预策略生成器
"""

import random
from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass

class TKIStrategy(Enum):
    COLLABORATING = "collaborating"    # 高关注自己&他人
    ACCOMMODATING = "accommodating"    # 低关注自己，高关注他人
    COMPETING = "competing"            # 高关注自己，低关注他人
    AVOIDING = "avoiding"              # 低关注自己&他人
    COMPROMISING = "compromising"      # 中等关注双方

class ConflictPhase(Enum):
    DIVERGENCE = "divergence"       # 分歧阶段
    ESCALATION = "escalation"       # 升级阶段
    DEADLOCK = "deadlock"          # 僵局阶段
    RESOLUTION = "resolution"       # 解决阶段

@dataclass
class InterventionTemplate:
    strategy: TKIStrategy
    phase: ConflictPhase
    template: str
    tone: str
    priority: int

class TKIInterventionGenerator:
    """基于TKI模型的干预生成器"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[TKIStrategy, List[InterventionTemplate]]:
        """初始化干预模板"""
        return {
            TKIStrategy.COLLABORATING: [
                InterventionTemplate(
                    TKIStrategy.COLLABORATING, ConflictPhase.DIVERGENCE,
                    "🤝 我看到大家都有很好的想法，也许我们可以整合一下不同的观点？",
                    "cooperative", 1
                ),
                InterventionTemplate(
                    TKIStrategy.COLLABORATING, ConflictPhase.ESCALATION,
                    "💡 让我们暂停一下，重新审视我们的共同目标。大家都希望{目标}，对吗？",
                    "refocusing", 2
                ),
                InterventionTemplate(
                    TKIStrategy.COLLABORATING, ConflictPhase.DEADLOCK,
                    "🔄 我们似乎陷入了循环讨论。不如尝试从不同角度来看这个问题？",
                    "reframing", 3
                ),
            ],
            
            TKIStrategy.ACCOMMODATING: [
                InterventionTemplate(
                    TKIStrategy.ACCOMMODATING, ConflictPhase.DIVERGENCE,
                    "🤗 我理解每个人的感受都很重要。{用户名}，你的想法是什么？",
                    "empathetic", 1
                ),
                InterventionTemplate(
                    TKIStrategy.ACCOMMODATING, ConflictPhase.ESCALATION,
                    "💙 我能感受到大家的情绪。让我们给彼此一些理解的空间。",
                    "supportive", 2
                ),
            ],
            
            TKIStrategy.COMPETING: [
                InterventionTemplate(
                    TKIStrategy.COMPETING, ConflictPhase.ESCALATION,
                    "⚡ 我们需要做出决定。基于当前信息，建议我们采用{方案}。",
                    "directive", 1
                ),
                InterventionTemplate(
                    TKIStrategy.COMPETING, ConflictPhase.DEADLOCK,
                    "🎯 时间紧迫，让我们专注于最关键的问题：{核心问题}。",
                    "focused", 2
                ),
            ],
            
            TKIStrategy.COMPROMISING: [
                InterventionTemplate(
                    TKIStrategy.COMPROMISING, ConflictPhase.DIVERGENCE,
                    "⚖️ 看起来我们都有合理的观点。有没有可能找到一个中间方案？",
                    "balanced", 1
                ),
                InterventionTemplate(
                    TKIStrategy.COMPROMISING, ConflictPhase.DEADLOCK,
                    "🤝 也许我们可以各退一步？{用户A}接受{让步1}，{用户B}接受{让步2}？",
                    "negotiating", 2
                ),
            ],
            
            TKIStrategy.AVOIDING: [
                InterventionTemplate(
                    TKIStrategy.AVOIDING, ConflictPhase.ESCALATION,
                    "⏸️ 大家似乎都需要一些时间思考。不如我们休息10分钟再继续？",
                    "cooling", 1
                ),
                InterventionTemplate(
                    TKIStrategy.AVOIDING, ConflictPhase.DEADLOCK,
                    "🕐 也许我们今天先到这里，给大家时间消化一下想法？",
                    "postponing", 2
                ),
            ],
        }
    
    def select_strategy(self, conflict_signals: Dict, context: Dict) -> TKIStrategy:
        """基于冲突信号和上下文选择TKI策略"""
        
        # 获取冲突阶段
        phase = self._assess_conflict_phase(conflict_signals, context)
        
        # 获取情绪强度
        emotion_intensity = conflict_signals.get("emotion", {}).get("value", 0.0)
        
        # 获取参与者数量和角色
        participants = context.get("participants", [])
        
        # 策略选择逻辑
        if phase == ConflictPhase.ESCALATION and emotion_intensity > 0.7:
            # 高情绪升级 - 使用包容或回避策略
            return random.choice([TKIStrategy.ACCOMMODATING, TKIStrategy.AVOIDING])
        
        elif phase == ConflictPhase.DEADLOCK:
            # 僵局 - 使用妥协或竞争策略
            return random.choice([TKIStrategy.COMPROMISING, TKIStrategy.COMPETING])
        
        elif len(participants) >= 3:
            # 多人讨论 - 优先协作
            return TKIStrategy.COLLABORATING
        
        else:
            # 默认使用协作策略
            return TKIStrategy.COLLABORATING
    
    def _assess_conflict_phase(self, signals: Dict, context: Dict) -> ConflictPhase:
        """评估冲突阶段"""
        lightweight_score = signals.get("lightweight", {}).get("value", 0.0)
        emotion_score = signals.get("emotion", {}).get("value", 0.0)
        turn_taking_issues = signals.get("turn_taking", {}).get("value", 0.0)
        
        # 简单的阶段判断逻辑
        if lightweight_score > 0.6 or emotion_score > 0.6:
            return ConflictPhase.ESCALATION
        elif turn_taking_issues > 0.3:
            return ConflictPhase.DEADLOCK
        elif lightweight_score > 0.3:
            return ConflictPhase.DIVERGENCE
        else:
            return ConflictPhase.RESOLUTION
    
    def generate_intervention(self, strategy: TKIStrategy, phase: ConflictPhase, 
                            context: Dict) -> str:
        """生成具体的干预消息"""
        
        # 获取对应的模板
        templates = self.templates.get(strategy, [])
        suitable_templates = [t for t in templates if t.phase == phase]
        
        if not suitable_templates:
            # 如果没有匹配的模板，使用该策略的第一个模板
            suitable_templates = templates[:1] if templates else []
        
        if not suitable_templates:
            # 默认消息
            return "🤔 让我们重新审视一下这个问题，找到最好的解决方案。"
        
        # 选择模板
        template = random.choice(suitable_templates)
        
        # 填充上下文变量
        message = self._fill_template(template.template, context)
        
        return message
    
    def _fill_template(self, template: str, context: Dict) -> str:
        """填充模板中的变量"""
        # 简单的变量替换
        participants = context.get("participants", [])
        
        if "{用户名}" in template and participants:
            template = template.replace("{用户名}", participants[0])
        
        if "{用户A}" in template and len(participants) >= 1:
            template = template.replace("{用户A}", participants[0])
        
        if "{用户B}" in template and len(participants) >= 2:
            template = template.replace("{用户B}", participants[1])
        
        if "{目标}" in template:
            template = template.replace("{目标}", context.get("goal", "完成任务"))
        
        if "{核心问题}" in template:
            template = template.replace("{核心问题}", context.get("core_issue", "当前分歧"))
        
        return template 