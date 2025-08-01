"""
基于Thomas冲突过程模型的智能干预系统
结合TKI策略的理论导向干预
"""

import asyncio
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConflictStage(Enum):
    """Thomas冲突过程模型的五个阶段"""
    FRUSTRATION = "frustration"           # 挫折感阶段
    CONCEPTUALIZATION = "conceptualization"  # 概念化阶段  
    BEHAVIOR = "behavior"                 # 行为阶段
    INTERACTION = "interaction"           # 互动阶段
    OUTCOMES = "outcomes"                 # 结果阶段

class InterventionTiming(Enum):
    """最佳干预时机"""
    PRE_BEHAVIOR = "pre_behavior"         # 意图与行为之间 (最佳时机)
    EARLY_INTERACTION = "early_interaction"  # 互动初期
    ESCALATION_POINT = "escalation_point"    # 升级节点
    DAMAGE_CONTROL = "damage_control"        # 损害控制

class TKIStrategy(Enum):
    """TKI冲突处理策略"""
    COLLABORATING = "collaborating"    # 高关注自己&他人 - 寻求双赢
    ACCOMMODATING = "accommodating"    # 低关注自己，高关注他人 - 满足对方
    COMPETING = "competing"            # 高关注自己，低关注他人 - 坚持立场
    AVOIDING = "avoiding"              # 低关注自己&他人 - 回避冲突
    COMPROMISING = "compromising"      # 中等关注双方 - 互相让步

@dataclass
class ConflictAnalysis:
    """冲突分析结果"""
    stage: ConflictStage
    intensity: float  # 0-1 冲突强度
    emotional_state: float  # 0-1 情绪激动程度
    escalation_risk: float  # 0-1 升级风险
    intervention_timing: InterventionTiming
    recommended_strategy: TKIStrategy
    confidence: float
    evidence: List[str]  # 判断依据
    timestamp: datetime

@dataclass
class ConversationContext:
    """对话上下文"""
    participant_count: int
    message_history: List[Dict[str, Any]]
    emotional_trajectory: List[float]  # 情绪变化轨迹
    conflict_indicators: List[str]
    power_dynamics: Dict[str, float]  # 发言权分布
    last_intervention: Optional[datetime]

class ThomasConflictAnalyzer:
    """基于Thomas模型的冲突分析器"""
    
    def __init__(self):
        self.stage_indicators = {
            ConflictStage.FRUSTRATION: {
                "keywords": ["挫折", "阻碍", "不公平", "受阻", "disappointed", "blocked", "unfair", "frustrated"],
                "patterns": ["我觉得", "感到", "让我", "使我", "I feel", "makes me", "I'm"],
                "emotional_markers": ["!", "？", "...", "emmm", "哎"],
                "weight": 0.3
            },
            ConflictStage.CONCEPTUALIZATION: {
                "keywords": ["我认为", "问题是", "关键在于", "重点是", "I think", "the issue", "the problem"],
                "patterns": ["这里的问题", "我的观点", "我觉得问题", "my point", "the way I see"],
                "reasoning_markers": ["因为", "所以", "但是", "然而", "because", "so", "but", "however"],
                "weight": 0.25
            },
            ConflictStage.BEHAVIOR: {
                "keywords": ["我要", "我会", "我决定", "必须", "I will", "I'm going to", "must", "have to"],
                "patterns": ["我不会", "我拒绝", "I won't", "I refuse", "I'm not going to"],
                "action_markers": ["行动", "做", "执行", "action", "do", "going to do"],
                "weight": 0.4
            },
            ConflictStage.INTERACTION: {
                "keywords": ["你说", "你的意思", "你认为", "you said", "you think", "you mean"],
                "patterns": ["来回", "争论", "辩论", "back and forth", "argue", "debate"],
                "interaction_markers": ["@", "回复", "针对", "reply", "respond to"],
                "weight": 0.35
            },
            ConflictStage.OUTCOMES: {
                "keywords": ["结果", "后果", "影响", "最终", "result", "consequence", "outcome", "finally"],
                "patterns": ["这样下去", "如果继续", "最后会", "if this continues", "will end up"],
                "finality_markers": ["完了", "结束", "不可能", "over", "impossible", "done"],
                "weight": 0.3
            }
        }
        
        self.intervention_timing_rules = {
            # 最佳干预时机：概念化→行为之间
            (ConflictStage.CONCEPTUALIZATION, ConflictStage.BEHAVIOR): InterventionTiming.PRE_BEHAVIOR,
            # 早期干预：挫折感→概念化
            (ConflictStage.FRUSTRATION, ConflictStage.CONCEPTUALIZATION): InterventionTiming.EARLY_INTERACTION,
            # 升级节点：行为→互动
            (ConflictStage.BEHAVIOR, ConflictStage.INTERACTION): InterventionTiming.ESCALATION_POINT,
            # 损害控制：互动→结果
            (ConflictStage.INTERACTION, ConflictStage.OUTCOMES): InterventionTiming.DAMAGE_CONTROL
        }
    
    def analyze_conflict_stage(self, message: str, context: ConversationContext) -> ConflictStage:
        """分析当前冲突阶段"""
        stage_scores = {}
        
        for stage, indicators in self.stage_indicators.items():
            score = 0.0
            
            # 关键词匹配
            for keyword in indicators["keywords"]:
                if keyword.lower() in message.lower():
                    score += 0.3
            
            # 模式匹配
            for pattern in indicators["patterns"]:
                if pattern.lower() in message.lower():
                    score += 0.4
            
            # 标记符匹配
            marker_key = list(indicators.keys())[2]  # 第三个key是标记符
            for marker in indicators[marker_key]:
                if marker in message:
                    score += 0.2
            
            # 应用权重
            stage_scores[stage] = score * indicators["weight"]
        
        # 返回得分最高的阶段
        return max(stage_scores, key=stage_scores.get)
    
    def calculate_escalation_risk(self, message: str, context: ConversationContext) -> float:
        """计算升级风险"""
        risk_factors = []
        
        # 情绪强度
        emotional_words = ["愤怒", "生气", "恼火", "angry", "furious", "mad"]
        emotion_count = sum(1 for word in emotional_words if word.lower() in message.lower())
        risk_factors.append(min(emotion_count * 0.2, 0.4))
        
        # 人身攻击
        personal_attacks = ["你总是", "你从不", "你这个", "you always", "you never", "you're such"]
        attack_count = sum(1 for attack in personal_attacks if attack.lower() in message.lower())
        risk_factors.append(min(attack_count * 0.3, 0.6))
        
        # 绝对化表达
        absolute_terms = ["完全", "绝对", "从来", "never", "always", "completely", "absolutely"]
        absolute_count = sum(1 for term in absolute_terms if term.lower() in message.lower())
        risk_factors.append(min(absolute_count * 0.15, 0.3))
        
        # 情绪轨迹趋势
        if len(context.emotional_trajectory) >= 3:
            recent_trend = context.emotional_trajectory[-3:]
            if all(recent_trend[i] < recent_trend[i+1] for i in range(len(recent_trend)-1)):
                risk_factors.append(0.3)  # 情绪持续上升
        
        return min(sum(risk_factors), 1.0)
    
    def determine_intervention_timing(self, current_stage: ConflictStage, 
                                    context: ConversationContext) -> InterventionTiming:
        """确定干预时机"""
        # 检查是否有历史阶段转换
        if len(context.message_history) >= 2:
            # 简化：基于当前阶段推断时机
            if current_stage == ConflictStage.FRUSTRATION:
                return InterventionTiming.EARLY_INTERACTION
            elif current_stage == ConflictStage.CONCEPTUALIZATION:
                return InterventionTiming.PRE_BEHAVIOR  # 最佳时机！
            elif current_stage == ConflictStage.BEHAVIOR:
                return InterventionTiming.ESCALATION_POINT
            elif current_stage == ConflictStage.INTERACTION:
                return InterventionTiming.DAMAGE_CONTROL
            else:
                return InterventionTiming.DAMAGE_CONTROL
        
        return InterventionTiming.EARLY_INTERACTION
    
    def select_tki_strategy(self, stage: ConflictStage, intensity: float, 
                          timing: InterventionTiming, context: ConversationContext) -> TKIStrategy:
        """基于冲突阶段和时机选择TKI策略"""
        
        # 基于阶段的策略选择
        stage_strategy_map = {
            ConflictStage.FRUSTRATION: {
                InterventionTiming.EARLY_INTERACTION: TKIStrategy.ACCOMMODATING,  # 理解挫折感
            },
            ConflictStage.CONCEPTUALIZATION: {
                InterventionTiming.PRE_BEHAVIOR: TKIStrategy.COLLABORATING,  # 最佳时机用协作
                InterventionTiming.EARLY_INTERACTION: TKIStrategy.COMPROMISING,
            },
            ConflictStage.BEHAVIOR: {
                InterventionTiming.ESCALATION_POINT: TKIStrategy.COMPROMISING,  # 寻求中间路线
                InterventionTiming.PRE_BEHAVIOR: TKIStrategy.COLLABORATING,
            },
            ConflictStage.INTERACTION: {
                InterventionTiming.DAMAGE_CONTROL: TKIStrategy.AVOIDING,  # 暂时降温
                InterventionTiming.ESCALATION_POINT: TKIStrategy.ACCOMMODATING,
            },
            ConflictStage.OUTCOMES: {
                InterventionTiming.DAMAGE_CONTROL: TKIStrategy.COLLABORATING,  # 重建关系
            }
        }
        
        # 获取推荐策略
        stage_strategies = stage_strategy_map.get(stage, {})
        base_strategy = stage_strategies.get(timing, TKIStrategy.COMPROMISING)
        
        # 根据强度调整策略
        if intensity > 0.8:
            # 高强度冲突：优先降温
            return TKIStrategy.AVOIDING if timing == InterventionTiming.DAMAGE_CONTROL else TKIStrategy.ACCOMMODATING
        elif intensity > 0.6:
            # 中等强度：寻求妥协
            return TKIStrategy.COMPROMISING
        elif intensity < 0.3:
            # 低强度：促进协作
            return TKIStrategy.COLLABORATING
        
        return base_strategy
    
    def analyze_conversation(self, message: str, author: str, 
                           context: ConversationContext) -> ConflictAnalysis:
        """综合分析对话冲突"""
        # 分析冲突阶段
        stage = self.analyze_conflict_stage(message, context)
        
        # 计算各项指标
        intensity = self.calculate_intensity(message, context)
        emotional_state = self.calculate_emotional_state(message)
        escalation_risk = self.calculate_escalation_risk(message, context)
        
        # 确定干预时机
        timing = self.determine_intervention_timing(stage, context)
        
        # 选择TKI策略
        strategy = self.select_tki_strategy(stage, intensity, timing, context)
        
        # 生成证据
        evidence = self.generate_evidence(message, stage, intensity)
        
        return ConflictAnalysis(
            stage=stage,
            intensity=intensity,
            emotional_state=emotional_state,
            escalation_risk=escalation_risk,
            intervention_timing=timing,
            recommended_strategy=strategy,
            confidence=min(intensity + emotional_state, 1.0),
            evidence=evidence,
            timestamp=datetime.now()
        )
    
    def calculate_intensity(self, message: str, context: ConversationContext) -> float:
        """计算冲突强度"""
        intensity_factors = []
        
        # 情绪词汇密度
        emotional_words = ["愤怒", "生气", "不满", "失望", "angry", "frustrated", "upset", "annoyed"]
        emotion_density = sum(1 for word in emotional_words if word.lower() in message.lower()) / max(len(message.split()), 1)
        intensity_factors.append(min(emotion_density * 3, 0.4))
        
        # 标点符号强度
        exclamation_count = message.count('!')
        question_count = message.count('?')
        intensity_factors.append(min((exclamation_count + question_count) * 0.1, 0.3))
        
        # 大写字母比例
        if len(message) > 0:
            caps_ratio = sum(1 for c in message if c.isupper()) / len(message)
            intensity_factors.append(min(caps_ratio * 0.5, 0.3))
        
        return min(sum(intensity_factors), 1.0)
    
    def calculate_emotional_state(self, message: str) -> float:
        """计算情绪状态"""
        emotional_indicators = {
            "high": ["愤怒", "恼火", "气死", "furious", "livid", "enraged"],
            "medium": ["生气", "不满", "郁闷", "angry", "upset", "annoyed"],
            "low": ["有点", "稍微", "略微", "slightly", "a bit", "somewhat"]
        }
        
        scores = {"high": 0, "medium": 0, "low": 0}
        for level, words in emotional_indicators.items():
            scores[level] = sum(1 for word in words if word.lower() in message.lower())
        
        # 加权计算
        emotional_score = (scores["high"] * 0.8 + scores["medium"] * 0.5 + scores["low"] * 0.2) / max(len(message.split()), 1)
        return min(emotional_score * 2, 1.0)
    
    def generate_evidence(self, message: str, stage: ConflictStage, intensity: float) -> List[str]:
        """生成判断依据"""
        evidence = []
        
        # 阶段判断依据
        evidence.append(f"冲突阶段: {stage.value} - 基于消息内容分析")
        
        # 强度判断依据
        if intensity > 0.7:
            evidence.append("高强度冲突 - 检测到强烈情绪表达")
        elif intensity > 0.4:
            evidence.append("中等强度冲突 - 存在明显分歧表达")
        else:
            evidence.append("低强度冲突 - 轻微情绪波动")
        
        # 具体证据
        if "!" in message:
            evidence.append("检测到感叹号 - 情绪激动指标")
        if any(word in message.lower() for word in ["你错了", "不同意", "反对", "wrong", "disagree"]):
            evidence.append("检测到直接反对表达")
        if any(word in message.lower() for word in ["愤怒", "生气", "angry", "mad"]):
            evidence.append("检测到情绪词汇")
        
        return evidence

class TheoryBasedInterventionGenerator:
    """基于理论的干预消息生成器"""
    
    def __init__(self):
        self.intervention_templates = {
            # 挫折感阶段 - 理解和验证情感
            (ConflictStage.FRUSTRATION, TKIStrategy.ACCOMMODATING): [
                "我能理解大家现在可能感到一些挫折。让我们先暂停一下，听听每个人的想法。",
                "看起来有些地方让人感到不舒服。我们可以一起找找原因，看看如何改善。",
                "感受到了一些紧张气氛。每个人的感受都很重要，我们来好好沟通一下。"
            ],
            
            # 概念化阶段 - 促进双方理解（最佳干预时机）
            (ConflictStage.CONCEPTUALIZATION, TKIStrategy.COLLABORATING): [
                "我注意到大家对这个问题有不同的看法。让我们尝试理解各自的观点，也许能找到更好的解决方案。",
                "看起来双方都有各自的考虑。我们可以分别说说自己的想法，然后看看是否有共同点。",
                "这个问题确实有多个角度。让我们一起探讨，看看能不能找到兼顾各方需求的方案。"
            ],
            
            (ConflictStage.CONCEPTUALIZATION, TKIStrategy.COMPROMISING): [
                "我看到大家都有合理的观点。也许我们可以找到一个中间方案，让每个人都能接受。",
                "双方的想法都有道理。让我们看看能否各退一步，找到平衡点。"
            ],
            
            # 行为阶段 - 引导建设性行为
            (ConflictStage.BEHAVIOR, TKIStrategy.COMPROMISING): [
                "我理解大家都想推进这件事。让我们先确定一些大家都能接受的基本原则，然后再往下讨论。",
                "看到大家都很积极地想解决问题。我们可以先商定一个大致方向，再细化具体做法。"
            ],
            
            # 互动阶段 - 冷却和重新定向
            (ConflictStage.INTERACTION, TKIStrategy.AVOIDING): [
                "我建议我们先暂停这个话题几分钟，让大家冷静一下，然后再继续讨论。",
                "看起来讨论有些激烈了。我们休息一下，稍后再以更平和的方式继续。"
            ],
            
            (ConflictStage.INTERACTION, TKIStrategy.ACCOMMODATING): [
                "我能感受到大家的热情，但让我们保持尊重的态度。每个人的想法都值得被听见。",
                "讨论很热烈，这很好。让我们确保每个人都有表达的机会，并且保持相互尊重。"
            ],
            
            # 结果阶段 - 修复关系和重建协作
            (ConflictStage.OUTCOMES, TKIStrategy.COLLABORATING): [
                "经过这次讨论，我们都学到了一些东西。让我们把注意力转向如何一起向前推进。",
                "虽然我们有分歧，但这说明大家都关心这个项目。现在我们来总结一下，看看下一步怎么做。"
            ]
        }
    
    def generate_intervention(self, analysis: ConflictAnalysis, context: ConversationContext) -> str:
        """基于分析结果生成干预消息"""
        key = (analysis.stage, analysis.recommended_strategy)
        templates = self.intervention_templates.get(key, [])
        
        if not templates:
            # 默认模板
            return f"我注意到讨论有些激烈。让我们保持冷静，继续建设性的对话。"
        
        # 选择模板（可以加入随机性或基于上下文的智能选择）
        template = templates[0]
        
        # 根据强度和时机调整语气
        if analysis.intensity > 0.8:
            template = "🛑 " + template  # 高强度加紧急标识
        elif analysis.intervention_timing == InterventionTiming.PRE_BEHAVIOR:
            template = "💡 " + template  # 最佳时机加建议标识
        
        # 添加理论依据（调试模式）
        debug_info = f"\n\n*[干预依据: {analysis.stage.value}阶段, {analysis.recommended_strategy.value}策略, 时机: {analysis.intervention_timing.value}]*"
        
        return template + debug_info

# 集成到主系统中
class EnhancedConflictMonitor:
    """增强的冲突监控系统 - 集成Thomas模型"""
    
    def __init__(self):
        self.thomas_analyzer = ThomasConflictAnalyzer()
        self.intervention_generator = TheoryBasedInterventionGenerator()
        self.conversation_contexts = {}  # 存储每个频道的对话上下文
    
    def get_or_create_context(self, channel_id: str) -> ConversationContext:
        """获取或创建对话上下文"""
        if channel_id not in self.conversation_contexts:
            self.conversation_contexts[channel_id] = ConversationContext(
                participant_count=0,
                message_history=[],
                emotional_trajectory=[],
                conflict_indicators=[],
                power_dynamics={},
                last_intervention=None
            )
        return self.conversation_contexts[channel_id]
    
    async def analyze_message(self, message: str, author: str, channel_id: str) -> Optional[str]:
        """分析消息并生成干预建议"""
        context = self.get_or_create_context(channel_id)
        
        # 更新上下文
        context.message_history.append({
            "content": message,
            "author": author,
            "timestamp": datetime.now()
        })
        
        # 保持历史记录在合理范围内
        if len(context.message_history) > 20:
            context.message_history = context.message_history[-20:]
        
        # 进行Thomas模型分析
        analysis = self.thomas_analyzer.analyze_conversation(message, author, context)
        
        # 更新情绪轨迹
        context.emotional_trajectory.append(analysis.emotional_state)
        if len(context.emotional_trajectory) > 10:
            context.emotional_trajectory = context.emotional_trajectory[-10:]
        
        # 判断是否需要干预
        should_intervene = self.should_intervene(analysis, context)
        
        if should_intervene:
            intervention_message = self.intervention_generator.generate_intervention(analysis, context)
            context.last_intervention = datetime.now()
            
            logger.info(f"🎯 冲突分析: 阶段={analysis.stage.value}, 强度={analysis.intensity:.2f}, 策略={analysis.recommended_strategy.value}")
            logger.info(f"⚡ 干预时机: {analysis.intervention_timing.value}")
            
            return intervention_message
        
        return None
    
    def should_intervene(self, analysis: ConflictAnalysis, context: ConversationContext) -> bool:
        """判断是否应该干预"""
        # 基本阈值检查
        if analysis.confidence < 0.3:
            return False
        
        # 冷却时间检查
        if context.last_intervention:
            time_since_last = datetime.now() - context.last_intervention
            if time_since_last < timedelta(seconds=30):
                return False
        
        # 基于Thomas模型的干预条件
        intervention_conditions = [
            # 最佳时机：概念化阶段，中等以上强度
            (analysis.stage == ConflictStage.CONCEPTUALIZATION and analysis.intensity > 0.4),
            
            # 高风险：行为阶段，高强度
            (analysis.stage == ConflictStage.BEHAVIOR and analysis.intensity > 0.6),
            
            # 紧急情况：互动阶段，很高强度
            (analysis.stage == ConflictStage.INTERACTION and analysis.intensity > 0.7),
            
            # 升级风险很高
            (analysis.escalation_risk > 0.8),
            
            # 情绪状态很高
            (analysis.emotional_state > 0.7)
        ]
        
        return any(intervention_conditions) 