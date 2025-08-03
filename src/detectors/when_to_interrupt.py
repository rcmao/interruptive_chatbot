"""
何时插话检测器 - 智能判断最佳干预时机
基于多种因素综合判断是否需要AI干预
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class InterruptionTrigger(Enum):
    """打断触发类型"""
    GENDER_IMBALANCE = "gender_imbalance"           # 性别不平衡
    EXPRESSION_DIFFICULTY = "expression_difficulty" # 表达困难
    CONVERSATION_DOMINANCE = "conversation_dominance" # 对话主导
    SILENCE_AFTER_FEMALE = "silence_after_female"   # 女性发言后沉默
    MALE_CONSECUTIVE = "male_consecutive"          # 男性连续发言
    FEMALE_INTERRUPTED = "female_interrupted"      # 女性被打断
    AGGRESSIVE_CONTEXT = "aggressive_context"      # 攻击性语境

@dataclass
class InterruptionDecision:
    """打断决策"""
    should_interrupt: bool
    confidence: float  # 0-1
    trigger_type: InterruptionTrigger
    urgency_level: int  # 1-5
    reasoning: str
    evidence: List[str]

class WhenToInterruptDetector:
    """何时插话检测器"""
    
    def __init__(self):
        self.conversation_history = []
        self.participant_stats = {}
        self.last_intervention_time = None
        self.intervention_cooldown = 30  # 30秒冷却时间
        
        # 配置参数
        self.config = {
            'min_messages_for_analysis': 3,  # 最少需要3条消息才开始分析
            'gender_imbalance_threshold': 0.7,  # 性别不平衡阈值
            'consecutive_male_threshold': 3,  # 连续男性发言阈值
            'silence_after_female_threshold': 10,  # 女性发言后沉默阈值（秒）
            'expression_difficulty_keywords': [
                '我觉得', '可能', '也许', '不太确定', '不知道', '嗯', '啊',
                'I think', 'maybe', 'perhaps', 'not sure', 'um', 'uh'
            ],
            'aggressive_keywords': [
                '你错了', '不对', '不可能', '你懂什么', '别废话',
                'you are wrong', 'impossible', 'what do you know', 'stop talking'
            ]
        }
    
    def analyze_message(self, message: str, author: str, gender: str, 
                       timestamp: datetime = None) -> InterruptionDecision:
        """分析消息并决定是否干预"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # 更新对话历史
        self._update_conversation_history(message, author, gender, timestamp)
        
        # 检查冷却时间
        if self._is_in_cooldown():
            return InterruptionDecision(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=InterruptionTrigger.GENDER_IMBALANCE,
                urgency_level=1,
                reasoning="处于干预冷却期",
                evidence=[]
            )
        
        # 检查是否有足够的消息进行分析
        if len(self.conversation_history) < self.config['min_messages_for_analysis']:
            return InterruptionDecision(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=InterruptionTrigger.GENDER_IMBALANCE,
                urgency_level=1,
                reasoning="消息数量不足，无法进行分析",
                evidence=[]
            )
        
        # 执行各种检测
        decisions = []
        
        # 1. 性别不平衡检测
        gender_decision = self._detect_gender_imbalance()
        if gender_decision.should_interrupt:
            decisions.append(gender_decision)
        
        # 2. 表达困难检测
        expression_decision = self._detect_expression_difficulty(message, gender)
        if expression_decision.should_interrupt:
            decisions.append(expression_decision)
        
        # 3. 对话主导检测
        dominance_decision = self._detect_conversation_dominance()
        if dominance_decision.should_interrupt:
            decisions.append(dominance_decision)
        
        # 4. 女性发言后沉默检测
        silence_decision = self._detect_silence_after_female(timestamp)
        if silence_decision.should_interrupt:
            decisions.append(silence_decision)
        
        # 5. 男性连续发言检测
        consecutive_decision = self._detect_male_consecutive()
        if consecutive_decision.should_interrupt:
            decisions.append(consecutive_decision)
        
        # 6. 女性被打断检测
        interrupted_decision = self._detect_female_interrupted(message, author, gender)
        if interrupted_decision.should_interrupt:
            decisions.append(interrupted_decision)
        
        # 7. 攻击性语境检测
        aggressive_decision = self._detect_aggressive_context(message)
        if aggressive_decision.should_interrupt:
            decisions.append(aggressive_decision)
        
        # 综合决策
        if not decisions:
            return InterruptionDecision(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=InterruptionTrigger.GENDER_IMBALANCE,
                urgency_level=1,
                reasoning="未检测到需要干预的情况",
                evidence=[]
            )
        
        # 选择最紧急的决策
        best_decision = max(decisions, key=lambda d: d.urgency_level)
        
        # 更新最后干预时间
        if best_decision.should_interrupt:
            self.last_intervention_time = timestamp
        
        return best_decision
    
    def _update_conversation_history(self, message: str, author: str, gender: str, timestamp: datetime):
        """更新对话历史"""
        entry = {
            'message': message,
            'author': author,
            'gender': gender,
            'timestamp': timestamp
        }
        self.conversation_history.append(entry)
        
        # 保持最近50条消息
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        # 更新参与者统计
        if author not in self.participant_stats:
            self.participant_stats[author] = {
                'gender': gender,
                'message_count': 0,
                'last_message_time': timestamp
            }
        
        self.participant_stats[author]['message_count'] += 1
        self.participant_stats[author]['last_message_time'] = timestamp
    
    def _is_in_cooldown(self) -> bool:
        """检查是否在冷却期内"""
        if self.last_intervention_time is None:
            return False
        
        time_since_last = datetime.now() - self.last_intervention_time
        return time_since_last.total_seconds() < self.intervention_cooldown
    
    def _detect_gender_imbalance(self) -> InterruptionDecision:
        """检测性别不平衡"""
        recent_messages = self.conversation_history[-10:]  # 最近10条消息
        
        male_messages = sum(1 for msg in recent_messages if msg['gender'] == 'male')
        female_messages = sum(1 for msg in recent_messages if msg['gender'] == 'female')
        total_messages = len(recent_messages)
        
        if total_messages == 0:
            return InterruptionDecision(False, 0.0, InterruptionTrigger.GENDER_IMBALANCE, 1, "无消息", [])
        
        male_ratio = male_messages / total_messages
        female_ratio = female_messages / total_messages
        
        # 如果男性发言比例过高且女性发言比例过低
        if male_ratio > self.config['gender_imbalance_threshold'] and female_ratio < 0.3:
            return InterruptionDecision(
                should_interrupt=True,
                confidence=0.8,
                trigger_type=InterruptionTrigger.GENDER_IMBALANCE,
                urgency_level=4,
                reasoning=f"性别不平衡：男性发言{male_ratio:.1%}，女性发言{female_ratio:.1%}",
                evidence=[f"男性消息: {male_messages}", f"女性消息: {female_messages}"]
            )
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.GENDER_IMBALANCE, 1, "性别比例正常", [])
    
    def _detect_expression_difficulty(self, message: str, gender: str) -> InterruptionDecision:
        """检测表达困难"""
        if gender != 'female':
            return InterruptionDecision(False, 0.0, InterruptionTrigger.EXPRESSION_DIFFICULTY, 1, "非女性发言", [])
        
        # 检查是否包含表达困难的关键词
        difficulty_count = 0
        for keyword in self.config['expression_difficulty_keywords']:
            if keyword.lower() in message.lower():
                difficulty_count += 1
        
        if difficulty_count >= 2:  # 包含2个或以上困难关键词
            return InterruptionDecision(
                should_interrupt=True,
                confidence=0.7,
                trigger_type=InterruptionTrigger.EXPRESSION_DIFFICULTY,
                urgency_level=3,
                reasoning="检测到女性表达困难信号",
                evidence=[f"困难关键词数量: {difficulty_count}", f"消息内容: {message[:50]}..."]
            )
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.EXPRESSION_DIFFICULTY, 1, "表达正常", [])
    
    def _detect_conversation_dominance(self) -> InterruptionDecision:
        """检测对话主导"""
        recent_messages = self.conversation_history[-8:]  # 最近8条消息
        
        if len(recent_messages) < 4:
            return InterruptionDecision(False, 0.0, InterruptionTrigger.CONVERSATION_DOMINANCE, 1, "消息不足", [])
        
        # 检查是否有单一参与者主导对话
        author_counts = {}
        for msg in recent_messages:
            author = msg['author']
            author_counts[author] = author_counts.get(author, 0) + 1
        
        max_count = max(author_counts.values())
        total_messages = len(recent_messages)
        
        if max_count / total_messages > 0.6:  # 单一参与者占60%以上
            dominant_author = max(author_counts, key=author_counts.get)
            dominant_gender = next(msg['gender'] for msg in recent_messages if msg['author'] == dominant_author)
            
            if dominant_gender == 'male':
                return InterruptionDecision(
                    should_interrupt=True,
                    confidence=0.8,
                    trigger_type=InterruptionTrigger.CONVERSATION_DOMINANCE,
                    urgency_level=4,
                    reasoning=f"男性参与者{dominant_author}主导对话",
                    evidence=[f"主导者消息数: {max_count}/{total_messages}", f"主导比例: {max_count/total_messages:.1%}"]
                )
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.CONVERSATION_DOMINANCE, 1, "对话主导正常", [])
    
    def _detect_silence_after_female(self, current_time: datetime) -> InterruptionDecision:
        """检测女性发言后沉默"""
        # 找到最近一次女性发言
        for msg in reversed(self.conversation_history):
            if msg['gender'] == 'female':
                time_since_female = current_time - msg['timestamp']
                if time_since_female.total_seconds() > self.config['silence_after_female_threshold']:
                    return InterruptionDecision(
                        should_interrupt=True,
                        confidence=0.9,
                        trigger_type=InterruptionTrigger.SILENCE_AFTER_FEMALE,
                        urgency_level=5,
                        reasoning=f"女性发言后已沉默{time_since_female.total_seconds():.0f}秒",
                        evidence=[f"最后女性发言: {msg['author']}", f"沉默时间: {time_since_female.total_seconds():.0f}秒"]
                    )
                break
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.SILENCE_AFTER_FEMALE, 1, "女性发言后无异常沉默", [])
    
    def _detect_male_consecutive(self) -> InterruptionDecision:
        """检测男性连续发言"""
        recent_messages = self.conversation_history[-self.config['consecutive_male_threshold']:]
        
        if len(recent_messages) < self.config['consecutive_male_threshold']:
            return InterruptionDecision(False, 0.0, InterruptionTrigger.MALE_CONSECUTIVE, 1, "消息不足", [])
        
        # 检查是否都是男性发言
        male_consecutive = all(msg['gender'] == 'male' for msg in recent_messages)
        
        if male_consecutive:
            return InterruptionDecision(
                should_interrupt=True,
                confidence=0.9,
                trigger_type=InterruptionTrigger.MALE_CONSECUTIVE,
                urgency_level=5,
                reasoning=f"检测到{len(recent_messages)}条连续男性发言",
                evidence=[f"连续男性发言数: {len(recent_messages)}", f"参与者: {', '.join(set(msg['author'] for msg in recent_messages))}"]
            )
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.MALE_CONSECUTIVE, 1, "无连续男性发言", [])
    
    def _detect_female_interrupted(self, message: str, author: str, gender: str) -> InterruptionDecision:
        """检测女性被打断"""
        if gender != 'male':
            return InterruptionDecision(False, 0.0, InterruptionTrigger.FEMALE_INTERRUPTED, 1, "非男性发言", [])
        
        # 检查是否有女性正在发言（通过消息长度和内容判断）
        recent_messages = self.conversation_history[-3:]
        for msg in recent_messages:
            if msg['gender'] == 'female' and msg['author'] != author:
                # 检查女性消息是否看起来被中断
                female_msg = msg['message']
                if len(female_msg) > 20 and not female_msg.endswith(('.', '!', '?')):
                    return InterruptionDecision(
                        should_interrupt=True,
                        confidence=0.8,
                        trigger_type=InterruptionTrigger.FEMALE_INTERRUPTED,
                        urgency_level=4,
                        reasoning=f"检测到女性{msg['author']}可能被打断",
                        evidence=[f"女性消息: {female_msg[:50]}...", f"男性打断者: {author}"]
                    )
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.FEMALE_INTERRUPTED, 1, "无女性被打断", [])
    
    def _detect_aggressive_context(self, message: str) -> InterruptionDecision:
        """检测攻击性语境"""
        aggressive_count = 0
        for keyword in self.config['aggressive_keywords']:
            if keyword.lower() in message.lower():
                aggressive_count += 1
        
        if aggressive_count >= 1:
            return InterruptionDecision(
                should_interrupt=True,
                confidence=0.9,
                trigger_type=InterruptionTrigger.AGGRESSIVE_CONTEXT,
                urgency_level=5,
                reasoning="检测到攻击性言论",
                evidence=[f"攻击性关键词数量: {aggressive_count}", f"消息内容: {message[:50]}..."]
            )
        
        return InterruptionDecision(False, 0.0, InterruptionTrigger.AGGRESSIVE_CONTEXT, 1, "无攻击性言论", [])
    
    def get_detection_summary(self) -> Dict:
        """获取检测摘要"""
        return {
            'total_messages': len(self.conversation_history),
            'participant_count': len(self.participant_stats),
            'gender_distribution': self._get_gender_distribution(),
            'last_intervention': self.last_intervention_time.isoformat() if self.last_intervention_time else None,
            'cooldown_active': self._is_in_cooldown()
        }
    
    def _get_gender_distribution(self) -> Dict:
        """获取性别分布"""
        male_count = sum(1 for msg in self.conversation_history if msg['gender'] == 'male')
        female_count = sum(1 for msg in self.conversation_history if msg['gender'] == 'female')
        total = len(self.conversation_history)
        
        return {
            'male': {'count': male_count, 'percentage': male_count/total if total > 0 else 0},
            'female': {'count': female_count, 'percentage': female_count/total if total > 0 else 0},
            'total': total
        } 