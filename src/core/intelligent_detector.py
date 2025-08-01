"""
智能上下文感知冲突检测系统
基于对话历史、情绪轨迹和微妙信号的综合判断
"""

import asyncio
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContextualMessage:
    """上下文化的消息"""
    content: str
    author: str
    timestamp: datetime
    emotion_score: float
    implicit_signals: List[str]
    response_pattern: str
    urgency_level: float

class ConversationContext:
    """对话上下文管理器"""
    
    def __init__(self, max_history: int = 10):
        self.message_history = deque(maxlen=max_history)
        self.emotion_trajectory = deque(maxlen=20)
        self.response_patterns = deque(maxlen=15)
        self.silence_periods = []
        self.conversation_flow = []
        self.participant_states = {}
        
    def add_message(self, message: ContextualMessage):
        """添加消息到上下文"""
        self.message_history.append(message)
        self.emotion_trajectory.append(message.emotion_score)
        self.response_patterns.append(message.response_pattern)
        
        # 更新参与者状态
        self.participant_states[message.author] = {
            'last_emotion': message.emotion_score,
            'last_message_time': message.timestamp,
            'recent_pattern': message.response_pattern
        }
    
    def get_emotion_trend(self, window: int = 5) -> float:
        """获取情绪趋势"""
        if len(self.emotion_trajectory) < 2:
            return 0.0
        
        recent_scores = list(self.emotion_trajectory)[-window:]
        if len(recent_scores) < 2:
            return 0.0
        
        # 计算趋势斜率
        x = list(range(len(recent_scores)))
        y = recent_scores
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def detect_conversation_breakdown(self) -> float:
        """检测对话breakdown信号"""
        if len(self.message_history) < 2:
            return 0.0
        
        breakdown_score = 0.0
        recent_messages = list(self.message_history)[-3:]
        
        # 1. 检测沉默期
        for i in range(1, len(recent_messages)):
            time_gap = (recent_messages[i].timestamp - recent_messages[i-1].timestamp).total_seconds()
            if time_gap > 60:  # 超过1分钟沉默
                breakdown_score += 0.3
        
        # 2. 检测短消息/符号回应增多
        short_responses = sum(1 for msg in recent_messages if len(msg.content.strip()) <= 5)
        if short_responses >= 2:
            breakdown_score += 0.4
        
        # 3. 检测回应模式变化
        if len(set(msg.response_pattern for msg in recent_messages)) == 1:
            # 回应模式单一化（如都是dismissive）
            if recent_messages[0].response_pattern in ['dismissive', 'defensive', 'frustrated']:
                breakdown_score += 0.3
        
        return min(breakdown_score, 1.0)

class IntelligentSignalDetector:
    """智能信号检测器"""
    
    def __init__(self):
        # 微妙信号模式库
        self.subtle_patterns = {
            # 情绪暗示
            'emotional_subtext': [
                (r'[.]{2,}', 0.3, "省略号表示犹豫/不满"),
                (r'[?]{2,}', 0.5, "多个问号表示困惑/不满"),
                (r'[!]{2,}', 0.6, "多个感叹号表示强烈情绪"),
                (r'^额+[.。]*$', 0.3, "语塞表达"),
                (r'^哦+[.。]*$', 0.4, "敷衍回应"),
                (r'^好吧[.。]*$', 0.4, "不情愿同意"),
                (r'^算了[.。]*$', 0.6, "放弃/失望"),
                (r'^呵呵+[.。]*$', 0.5, "冷笑/不屑"),
            ],
            
            # 回避模式
            'avoidance_patterns': [
                (r'忙|有事|不在', 0.3, "回避借口"),
                (r'随便|都行|无所谓', 0.3, "消极回应"),
                (r'我不知道|不清楚|不确定', 0.2, "推卸责任"),
            ],
            
            # 升级信号
            'escalation_signals': [
                (r'又|还是|还在|仍然', 0.4, "重复性抱怨"),
                (r'为什么|怎么|凭什么', 0.4, "质疑态度"),
                (r'总是|从来|永远|一直', 0.5, "绝对化表达"),
            ],
            
            # 压力信号
            'stress_indicators': [
                (r'压力|累|疲|忙死|忙疯', 0.3, "压力表达"),
                (r'受不了|承受不了|太多', 0.4, "承受极限"),
                (r'没时间|时间不够|赶不上', 0.3, "时间压力"),
            ]
        }
        
        # 上下文敏感关键词
        self.context_sensitive_keywords = {
            'project_stress': ['deadline', 'presentation', 'ppt', '汇报', '展示', '项目'],
            'responsibility': ['负责', '任务', '部分', '工作', 'responsible', 'task'],
            'collaboration': ['合作', '配合', '团队', 'team', 'together', '一起'],
            'time_pressure': ['时间', '急', '快', 'time', 'urgent', 'hurry']
        }
    
    def analyze_subtle_signals(self, message: str) -> Tuple[float, List[str]]:
        """分析微妙信号"""
        total_score = 0.0
        detected_signals = []
        
        # 检测各种微妙模式
        for category, patterns in self.subtle_patterns.items():
            for pattern, weight, description in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    total_score += weight
                    detected_signals.append(f"{category}: {description}")
        
        return min(total_score, 1.0), detected_signals
    
    def analyze_response_pattern(self, message: str, previous_messages: List[str]) -> str:
        """分析回应模式"""
        message_lower = message.lower().strip()
        
        # 极短回应
        if len(message_lower) <= 3:
            if message_lower in ['ok', '好', '嗯', 'um', 'eh']:
                return 'minimal_acknowledgment'
            elif '?' in message:
                return 'confused_question'
            else:
                return 'dismissive'
        
        # 防御性回应
        defensive_indicators = ['不是', '没有', '不对', '但是', 'but', 'not', "didn't"]
        if any(indicator in message_lower for indicator in defensive_indicators):
            return 'defensive'
        
        # 解释性回应
        explanation_indicators = ['因为', '由于', '所以', 'because', 'since', 'due to']
        if any(indicator in message_lower for indicator in explanation_indicators):
            return 'explanatory'
        
        # 合作性回应
        cooperative_indicators = ['我们', '一起', '配合', 'we', 'together', 'cooperate']
        if any(indicator in message_lower for indicator in cooperative_indicators):
            return 'cooperative'
        
        # 挫折性回应
        frustration_indicators = ['为什么', '怎么', '又', 'why', 'how', 'again']
        if any(indicator in message_lower for indicator in frustration_indicators):
            return 'frustrated'
        
        return 'neutral'
    
    def calculate_contextual_urgency(self, message: str, context: ConversationContext) -> float:
        """计算上下文紧急度"""
        urgency = 0.0
        
        # 1. 基于情绪轨迹
        emotion_trend = context.get_emotion_trend()
        if emotion_trend > 0.1:  # 情绪上升趋势
            urgency += 0.3
        
        # 2. 基于对话breakdown信号
        breakdown_score = context.detect_conversation_breakdown()
        urgency += breakdown_score * 0.4
        
        # 3. 基于时间敏感性
        time_sensitive_words = ['明天', '今天', '马上', 'tomorrow', 'today', 'now', 'urgent']
        if any(word in message.lower() for word in time_sensitive_words):
            urgency += 0.3
        
        # 4. 基于项目关键节点
        critical_moments = ['presentation', 'deadline', 'meeting', '汇报', '截止', '会议']
        if any(moment in message.lower() for moment in critical_moments):
            urgency += 0.2
        
        return min(urgency, 1.0)

class ContextAwareConflictDetector:
    """上下文感知冲突检测器"""
    
    def __init__(self):
        self.signal_detector = IntelligentSignalDetector()
        self.contexts = {}  # 每个频道的上下文
        
        # 动态阈值系统
        self.base_threshold = 0.35
        self.context_modifiers = {
            'high_stress_conversation': -0.1,  # 降低阈值，更敏感
            'project_deadline_near': -0.15,
            'repeated_breakdown_signals': -0.2,
            'first_signs_of_tension': -0.05
        }
    
    def get_context(self, channel_id: str) -> ConversationContext:
        """获取频道上下文"""
        if channel_id not in self.contexts:
            self.contexts[channel_id] = ConversationContext()
        return self.contexts[channel_id]
    
    async def intelligent_conflict_detection(self, message: str, author: str, channel_id: str) -> Dict:
        """智能冲突检测"""
        context = self.get_context(channel_id)
        
        # 1. 分析微妙信号
        subtle_score, subtle_signals = self.signal_detector.analyze_subtle_signals(message)
        
        # 2. 分析回应模式
        previous_messages = [msg.content for msg in list(context.message_history)[-3:]]
        response_pattern = self.signal_detector.analyze_response_pattern(message, previous_messages)
        
        # 3. 计算上下文紧急度
        contextual_urgency = self.signal_detector.calculate_contextual_urgency(message, context)
        
        # 4. 基础情绪分析
        base_emotion_score = self._basic_emotion_analysis(message)
        
        # 5. 综合评分
        composite_score = self._calculate_composite_score(
            subtle_score, base_emotion_score, contextual_urgency, response_pattern, context
        )
        
        # 6. 动态阈值调整
        adjusted_threshold = self._calculate_dynamic_threshold(context, response_pattern)
        
        # 7. 创建上下文化消息
        contextual_msg = ContextualMessage(
            content=message,
            author=author,
            timestamp=datetime.now(),
            emotion_score=composite_score,
            implicit_signals=subtle_signals,
            response_pattern=response_pattern,
            urgency_level=contextual_urgency
        )
        
        # 8. 更新上下文
        context.add_message(contextual_msg)
        
        # 9. 判断是否需要干预
        should_intervene = composite_score > adjusted_threshold
        
        # 10. 生成解释
        explanation = self._generate_detection_explanation(
            message, composite_score, adjusted_threshold, subtle_signals, 
            response_pattern, contextual_urgency
        )
        
        logger.info(f"🔍 智能检测: '{message[:30]}...'")
        logger.info(f"   综合分数: {composite_score:.3f} (阈值: {adjusted_threshold:.3f})")
        logger.info(f"   微妙信号: {', '.join(subtle_signals) if subtle_signals else '无'}")
        logger.info(f"   回应模式: {response_pattern}")
        logger.info(f"   上下文紧急度: {contextual_urgency:.3f}")
        logger.info(f"   决策: {'🚨 需要干预' if should_intervene else '✅ 继续观察'}")
        
        return {
            'should_intervene': should_intervene,
            'confidence': composite_score,
            'threshold_used': adjusted_threshold,
            'subtle_signals': subtle_signals,
            'response_pattern': response_pattern,
            'contextual_urgency': contextual_urgency,
            'explanation': explanation,
            'emotion_trend': context.get_emotion_trend(),
            'conversation_health': 1.0 - context.detect_conversation_breakdown()
        }
    
    def _basic_emotion_analysis(self, message: str) -> float:
        """基础情绪分析"""
        score = 0.0
        
        # 强烈情绪词汇
        strong_emotions = ['愤怒', '生气', '愤慨', 'angry', 'furious', 'mad']
        score += sum(0.4 for word in strong_emotions if word in message.lower())
        
        # 中等情绪词汇
        medium_emotions = ['不满', '担心', '失望', 'upset', 'worried', 'disappointed']
        score += sum(0.3 for word in medium_emotions if word in message.lower())
        
        # 轻微情绪词汇
        mild_emotions = ['有点', '稍微', '略微', 'slightly', 'a bit', 'somewhat']
        score += sum(0.2 for word in mild_emotions if word in message.lower())
        
        return min(score, 1.0)
    
    def _calculate_composite_score(self, subtle_score: float, emotion_score: float, 
                                 urgency: float, pattern: str, context: ConversationContext) -> float:
        """计算综合分数"""
        # 基础分数
        base_score = (subtle_score * 0.4 + emotion_score * 0.3 + urgency * 0.3)
        
        # 回应模式调整
        pattern_modifiers = {
            'defensive': 0.2,
            'frustrated': 0.3,
            'dismissive': 0.25,
            'minimal_acknowledgment': 0.15,
            'confused_question': 0.1,
            'cooperative': -0.1,
            'explanatory': -0.05,
            'neutral': 0.0
        }
        
        pattern_adjustment = pattern_modifiers.get(pattern, 0.0)
        
        # 情绪趋势调整
        emotion_trend = context.get_emotion_trend()
        trend_adjustment = emotion_trend * 0.2  # 上升趋势增加分数
        
        # 对话breakdown调整
        breakdown_score = context.detect_conversation_breakdown()
        breakdown_adjustment = breakdown_score * 0.3
        
        final_score = base_score + pattern_adjustment + trend_adjustment + breakdown_adjustment
        
        return max(0.0, min(final_score, 1.0))
    
    def _calculate_dynamic_threshold(self, context: ConversationContext, pattern: str) -> float:
        """计算动态阈值"""
        threshold = self.base_threshold
        
        # 基于对话健康状况调整
        conversation_health = 1.0 - context.detect_conversation_breakdown()
        if conversation_health < 0.7:
            threshold -= 0.1  # 对话质量下降，降低干预阈值
        
        # 基于情绪趋势调整
        emotion_trend = context.get_emotion_trend()
        if emotion_trend > 0.2:
            threshold -= 0.05  # 情绪持续上升，更早干预
        
        # 基于回应模式调整
        if pattern in ['defensive', 'dismissive', 'frustrated']:
            threshold -= 0.05  # 负面模式，提前干预
        
        return max(0.15, threshold)  # 最低阈值0.15
    
    def _generate_detection_explanation(self, message: str, score: float, threshold: float,
                                      signals: List[str], pattern: str, urgency: float) -> str:
        """生成检测说明"""
        explanation_parts = []
        
        if score > threshold:
            explanation_parts.append(f"检测到需要干预 (分数: {score:.3f} > 阈值: {threshold:.3f})")
        else:
            explanation_parts.append(f"暂无需干预 (分数: {score:.3f} ≤ 阈值: {threshold:.3f})")
        
        if signals:
            explanation_parts.append(f"微妙信号: {', '.join(signals)}")
        
        if pattern != 'neutral':
            explanation_parts.append(f"回应模式: {pattern}")
        
        if urgency > 0.3:
            explanation_parts.append(f"上下文紧急度: {urgency:.2f}")
        
        return " | ".join(explanation_parts)

# 集成到主机器人系统
class EnhancedThomasBot:
    """增强版Thomas冲突干预机器人"""
    
    def __init__(self):
        self.intelligent_detector = ContextAwareConflictDetector()
    
    async def process_message(self, message: str, author: str, channel_id: str) -> Optional[str]:
        """处理消息"""
        # 使用智能检测器
        detection_result = await self.intelligent_detector.intelligent_conflict_detection(
            message, author, channel_id
        )
        
        if detection_result['should_intervene']:
            # 基于检测结果生成合适的干预
            intervention = self._generate_contextual_intervention(detection_result)
            return intervention
        
        return None
    
    def _generate_contextual_intervention(self, detection_result: Dict) -> str:
        """生成上下文化的干预"""
        pattern = detection_result['response_pattern']
        urgency = detection_result['contextual_urgency']
        
        if urgency > 0.6:
            return "🚨 我注意到对话变得紧张。让我们暂停一下，重新聚焦在解决问题上。"
        elif pattern == 'frustrated':
            return "💡 我感受到一些挫折感。也许我们可以换个角度来看这个问题？"
        elif pattern == 'defensive':
            return "🤝 我理解大家都有自己的考虑。让我们确保每个人的观点都被听到。"
        elif pattern == 'dismissive':
            return "⚡ 看起来需要更多的沟通。我们来澄清一下彼此的期望？"
        elif 'emotional_subtext' in str(detection_result['subtle_signals']):
            return "🔍 我注意到一些微妙的信号。如果有什么困扰，我们可以开诚布公地讨论。"
        else:
            return "💬 让我们保持建设性的对话，确保每个人都感到被理解。" 