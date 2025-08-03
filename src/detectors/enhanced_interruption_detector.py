"""
增强的打断检测器 - 使用GPT实时上下文评估
结合规则检测和GPT语义分析，提供更智能的干预判断
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

class EnhancedInterruptionTrigger(Enum):
    """增强的打断触发类型"""
    FEMALE_INTERRUPTED = "female_interrupted"      # 女性被打断
    FEMALE_IGNORED = "female_ignored"              # 女性被忽视
    MALE_DOMINANCE = "male_dominance"              # 男性主导对话
    MALE_CONSECUTIVE = "male_consecutive"          # 男性连续发言
    GENDER_IMBALANCE = "gender_imbalance"          # 性别不平衡
    EXPRESSION_DIFFICULTY = "expression_difficulty"  # 表达困难
    AGGRESSIVE_CONTEXT = "aggressive_context"      # 攻击性语境

@dataclass
class EnhancedInterruptionDecision:
    """增强的打断决策"""
    should_interrupt: bool
    confidence: float  # 0-1
    trigger_type: EnhancedInterruptionTrigger
    urgency_level: int  # 1-5
    reasoning: str
    evidence: List[str]
    gpt_analysis: Optional[Dict] = None
    context_score: float = 0.0

class GPTContextAnalyzer:
    """GPT上下文分析器"""
    
    def __init__(self):
        self.context_window = 10  # 分析最近10条消息
        self.intervention_threshold = 0.7  # 干预阈值
    
    async def analyze_context(self, conversation_history, current_message, current_author, current_gender):
        """使用GPT分析当前对话上下文"""
        
        # 格式化对话历史
        formatted_history = self._format_conversation_history(conversation_history)
        
        prompt = f"""
        分析以下对话上下文，评估是否需要AI干预：
        
        对话历史：
        {formatted_history}
        
        当前消息：{current_message} (发送者: {current_author}, 性别: {current_gender})
        
        请从以下维度评估（0-1分）：
        1. 性别不平等程度 (gender_inequality)
        2. 攻击性/冲突程度 (aggressive_level)
        3. 表达困难程度 (expression_difficulty)
        4. 打断/忽视程度 (interruption_level)
        5. 整体干预必要性 (overall_intervention_score)
        
        返回JSON格式：
        {{
            "gender_inequality": 0.8,
            "aggressive_level": 0.9,
            "expression_difficulty": 0.3,
            "interruption_level": 0.7,
            "overall_intervention_score": 0.8,
            "reasoning": "检测到明显的性别不平等和攻击性言论",
            "suggested_strategy": "competing",
            "trigger_type": "aggressive_context"
        }}
        """
        
        # 模拟GPT分析（实际使用时替换为真实的GPT调用）
        analysis_result = await self._simulate_gpt_analysis(prompt, current_message)
        return analysis_result
    
    def _format_conversation_history(self, conversation_history):
        """格式化对话历史"""
        if not conversation_history:
            return "无对话历史"
        
        formatted = []
        for msg in conversation_history[-self.context_window:]:
            timestamp = msg.get('timestamp', '').strftime('%H:%M:%S') if hasattr(msg.get('timestamp', ''), 'strftime') else ''
            formatted.append(f"[{timestamp}] {msg.get('author', 'Unknown')} ({msg.get('gender', 'unknown')}): {msg.get('message', '')}")
        
        return "\n".join(formatted)
    
    async def _simulate_gpt_analysis(self, prompt, current_message):
        """模拟GPT分析（实际使用时替换为真实的GPT调用）"""
        
        # 基于关键词的简单分析
        analysis = {
            "gender_inequality": 0.0,
            "aggressive_level": 0.0,
            "expression_difficulty": 0.0,
            "interruption_level": 0.0,
            "overall_intervention_score": 0.0,
            "reasoning": "正常对话",
            "suggested_strategy": "collaborating",
            "trigger_type": "none"
        }
        
        # 检测攻击性言论
        aggressive_keywords = ['你错了', '不对', '不可能', '你懂什么', '别废话', '闭嘴']
        aggressive_count = sum(1 for keyword in aggressive_keywords if keyword in current_message.lower())
        if aggressive_count > 0:
            analysis["aggressive_level"] = min(0.9, aggressive_count * 0.3)
            analysis["trigger_type"] = "aggressive_context"
            analysis["suggested_strategy"] = "competing"
            analysis["reasoning"] = "检测到攻击性言论"
        
        # 检测表达困难
        difficulty_keywords = ['我觉得', '可能', '也许', '不太确定', '不知道', '嗯', '啊']
        difficulty_count = sum(1 for keyword in difficulty_keywords if keyword in current_message.lower())
        if difficulty_count >= 2:
            analysis["expression_difficulty"] = min(0.8, difficulty_count * 0.2)
            analysis["trigger_type"] = "expression_difficulty"
            analysis["suggested_strategy"] = "accommodating"
            analysis["reasoning"] = "检测到表达困难"
        
        # 计算整体干预分数
        analysis["overall_intervention_score"] = max(
            analysis["gender_inequality"],
            analysis["aggressive_level"],
            analysis["expression_difficulty"],
            analysis["interruption_level"]
        )
        
        return analysis

class EnhancedInterruptionDetector:
    """增强的打断检测器"""
    
    def __init__(self):
        self.conversation_history = []
        self.participant_stats = {}
        self.last_intervention_time = None
        self.intervention_cooldown = 30  # 30秒冷却时间
        self.gpt_analyzer = GPTContextAnalyzer()
        
        # 配置参数
        self.config = {
            'min_messages_for_analysis': 3,  # 最少需要3条消息才开始分析
            'gender_imbalance_threshold': 0.7,  # 性别不平衡阈值
            'consecutive_male_threshold': 3,  # 连续男性发言阈值
            'silence_after_female_threshold': 10,  # 女性发言后沉默阈值（秒）
            'gpt_analysis_weight': 0.6,  # GPT分析权重
            'rule_based_weight': 0.4,  # 规则检测权重
        }
    
    async def analyze_message(self, message: str, author: str, gender: str, 
                            timestamp: datetime = None) -> EnhancedInterruptionDecision:
        """分析消息并决定是否干预"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # 更新对话历史
        self._update_conversation_history(message, author, gender, timestamp)
        
        # 检查冷却时间
        if self._is_in_cooldown():
            return EnhancedInterruptionDecision(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=EnhancedInterruptionTrigger.GENDER_IMBALANCE,
                urgency_level=1,
                reasoning="处于干预冷却期",
                evidence=[]
            )
        
        # 检查是否有足够的消息进行分析
        if len(self.conversation_history) < self.config['min_messages_for_analysis']:
            return EnhancedInterruptionDecision(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=EnhancedInterruptionTrigger.GENDER_IMBALANCE,
                urgency_level=1,
                reasoning="消息数量不足，无法进行分析",
                evidence=[]
            )
        
        # 1. 规则基础检测
        rule_decision = self._rule_based_detection(message, author, gender)
        
        # 2. GPT上下文分析
        gpt_analysis = await self.gpt_analyzer.analyze_context(
            self.conversation_history, message, author, gender
        )
        
        # 3. 综合决策
        final_decision = self._combine_decisions(rule_decision, gpt_analysis)
        
        # 更新最后干预时间
        if final_decision.should_interrupt:
            self.last_intervention_time = timestamp
        
        return final_decision
    
    def _rule_based_detection(self, message: str, author: str, gender: str) -> Dict:
        """规则基础检测"""
        detection_results = {
            'should_interrupt': False,
            'confidence': 0.0,
            'trigger_type': None,
            'urgency_level': 1,
            'reasoning': "未检测到需要干预的情况",
            'evidence': []
        }
        
        # 检测攻击性语境
        aggressive_keywords = ['你错了', '不对', '不可能', '你懂什么', '别废话']
        aggressive_count = sum(1 for keyword in aggressive_keywords if keyword.lower() in message.lower())
        if aggressive_count >= 1:
            detection_results.update({
                'should_interrupt': True,
                'confidence': 0.9,
                'trigger_type': EnhancedInterruptionTrigger.AGGRESSIVE_CONTEXT.value,
                'urgency_level': 5,
                'reasoning': "检测到攻击性言论",
                'evidence': [f"攻击性关键词数量: {aggressive_count}"]
            })
            return detection_results
        
        # 检测男性连续发言
        recent_messages = self.conversation_history[-3:]
        if len(recent_messages) >= 3:
            male_consecutive = all(msg['gender'] == 'male' for msg in recent_messages)
            if male_consecutive:
                detection_results.update({
                    'should_interrupt': True,
                    'confidence': 0.8,
                    'trigger_type': EnhancedInterruptionTrigger.MALE_CONSECUTIVE.value,
                    'urgency_level': 4,
                    'reasoning': "检测到连续男性发言",
                    'evidence': [f"连续男性发言数: {len(recent_messages)}"]
                })
                return detection_results
        
        # 检测女性被打断
        if gender == 'male':
            recent_messages = self.conversation_history[-3:]
            for msg in recent_messages:
                if msg['gender'] == 'female' and msg['author'] != author:
                    female_msg = msg['message']
                    if len(female_msg) > 20 and not female_msg.endswith(('.', '!', '?')):
                        detection_results.update({
                            'should_interrupt': True,
                            'confidence': 0.8,
                            'trigger_type': EnhancedInterruptionTrigger.FEMALE_INTERRUPTED.value,
                            'urgency_level': 4,
                            'reasoning': f"检测到女性{msg['author']}可能被打断",
                            'evidence': [f"女性消息: {female_msg[:50]}...", f"男性打断者: {author}"]
                        })
                        return detection_results
        
        return detection_results
    
    def _combine_decisions(self, rule_decision: Dict, gpt_analysis: Dict) -> EnhancedInterruptionDecision:
        """综合规则检测和GPT分析结果"""
        
        # 计算综合分数
        rule_score = rule_decision['confidence'] if rule_decision['should_interrupt'] else 0.0
        gpt_score = gpt_analysis.get('overall_intervention_score', 0.0)
        
        combined_score = (
            rule_score * self.config['rule_based_weight'] +
            gpt_score * self.config['gpt_analysis_weight']
        )
        
        # 决定是否干预
        should_interrupt = combined_score > 0.6 or rule_decision['should_interrupt']
        
        # 确定触发类型
        trigger_type = self._determine_trigger_type(rule_decision, gpt_analysis)
        
        # 确定紧急程度
        urgency_level = self._determine_urgency_level(rule_decision, gpt_analysis)
        
        # 生成推理
        reasoning = self._generate_reasoning(rule_decision, gpt_analysis)
        
        return EnhancedInterruptionDecision(
            should_interrupt=should_interrupt,
            confidence=combined_score,
            trigger_type=trigger_type,
            urgency_level=urgency_level,
            reasoning=reasoning,
            evidence=rule_decision.get('evidence', []),
            gpt_analysis=gpt_analysis,
            context_score=gpt_score
        )
    
    def _determine_trigger_type(self, rule_decision: Dict, gpt_analysis: Dict) -> EnhancedInterruptionTrigger:
        """确定触发类型"""
        if rule_decision['trigger_type']:
            return EnhancedInterruptionTrigger(rule_decision['trigger_type'])
        
        gpt_trigger = gpt_analysis.get('trigger_type', 'none')
        if gpt_trigger != 'none':
            trigger_map = {
                'aggressive_context': EnhancedInterruptionTrigger.AGGRESSIVE_CONTEXT,
                'expression_difficulty': EnhancedInterruptionTrigger.EXPRESSION_DIFFICULTY,
                'female_interrupted': EnhancedInterruptionTrigger.FEMALE_INTERRUPTED,
                'male_dominance': EnhancedInterruptionTrigger.MALE_DOMINANCE
            }
            return trigger_map.get(gpt_trigger, EnhancedInterruptionTrigger.GENDER_IMBALANCE)
        
        return EnhancedInterruptionTrigger.GENDER_IMBALANCE
    
    def _determine_urgency_level(self, rule_decision: Dict, gpt_analysis: Dict) -> int:
        """确定紧急程度"""
        rule_urgency = rule_decision.get('urgency_level', 1)
        gpt_score = gpt_analysis.get('overall_intervention_score', 0.0)
        
        # 根据GPT分数确定紧急程度
        if gpt_score > 0.8:
            gpt_urgency = 5
        elif gpt_score > 0.6:
            gpt_urgency = 4
        elif gpt_score > 0.4:
            gpt_urgency = 3
        else:
            gpt_urgency = 1
        
        return max(rule_urgency, gpt_urgency)
    
    def _generate_reasoning(self, rule_decision: Dict, gpt_analysis: Dict) -> str:
        """生成推理说明"""
        if rule_decision['should_interrupt']:
            return rule_decision['reasoning']
        
        gpt_reasoning = gpt_analysis.get('reasoning', '')
        if gpt_reasoning and gpt_analysis.get('overall_intervention_score', 0.0) > 0.6:
            return f"GPT分析: {gpt_reasoning}"
        
        return "未检测到需要干预的情况"
    
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
    
    def get_detection_summary(self) -> Dict:
        """获取检测摘要"""
        return {
            'total_messages': len(self.conversation_history),
            'participant_count': len(self.participant_stats),
            'gender_distribution': self._get_gender_distribution(),
            'last_intervention': self.last_intervention_time.isoformat() if self.last_intervention_time else None,
            'cooldown_active': self._is_in_cooldown(),
            'gpt_analysis_enabled': True,
            'detection_method': 'hybrid'
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