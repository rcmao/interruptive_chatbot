"""
基于性别结构性边缘化行为的打断时机检测器
专门检测三类打断时机：结构性边缘化、表达困难信号、潜在攻击性语境
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class InterruptionType(Enum):
    """打断类型枚举"""
    STRUCTURAL_MARGINALIZATION = "structural_marginalization"  # 结构性边缘化
    EXPRESSION_DIFFICULTY = "expression_difficulty"           # 表达困难信号
    POTENTIAL_AGGRESSION = "potential_aggression"            # 潜在攻击性语境

class MarginalizationPattern(Enum):
    """边缘化模式枚举"""
    MALE_DOMINANCE = "male_dominance"              # 男性连续互动，女性未被接话
    FEMALE_IGNORED = "female_ignored"              # 女性发言后无人回应
    FEMALE_INTERRUPTED = "female_interrupted"      # 女性说话过程中被打断
    FEMALE_CREDIT_STOLEN = "female_credit_stolen"  # 女性观点被抢答或归为他人
    FEMALE_DEROGATED = "female_derogated"          # 女性表达被转移打断

class ExpressionDifficultyPattern(Enum):
    """表达困难模式枚举"""
    HESITATION = "hesitation"                      # 犹豫、卡顿、词不达意
    LACK_AUTHORITY = "lack_authority"              # 缺乏话语权威，遭遇冷场
    MOCKED_QUESTION = "mocked_question"            # 提问遭遇嘲讽
    TERMINOLOGY_BOMBARDMENT = "terminology_bombardment"  # 术语轰炸

class AggressionPattern(Enum):
    """攻击性模式枚举"""
    GENDER_STEREOTYPE = "gender_stereotype"        # 性别定型言论
    EXPRESSION_MOCKED = "expression_mocked"        # 表达被当作笑点
    SILENCE_MOCKED = "silence_mocked"              # 嘲笑沉默

@dataclass
class InterruptionTrigger:
    """打断时机数据结构"""
    interruption_type: InterruptionType
    pattern: Optional[Enum]
    confidence: float
    evidence: List[str]
    urgency_level: int  # 1-5级，5级最紧急
    recommended_action: str
    timestamp: datetime

class GenderBasedInterruptionDetector:
    """基于性别结构性边缘化的打断时机检测器"""
    
    def __init__(self):
        self.conversation_history = []
        self.participant_gender = {}  # 参与者性别映射
        self.interruption_triggers = []
        
        # 初始化检测模式
        self._initialize_detection_patterns()
    
    def _initialize_detection_patterns(self):
        """初始化检测模式"""
        
        # 一类：结构性边缘化行为模式
        self.structural_patterns = {
            MarginalizationPattern.MALE_DOMINANCE: {
                "keywords": ["男生", "男人", "male", "men"],
                "context_patterns": [
                    r"男.*男.*连续.*轮",
                    r"male.*male.*consecutive.*turns"
                ],
                "threshold": 0.7
            },
            
            MarginalizationPattern.FEMALE_IGNORED: {
                "keywords": ["女生", "女人", "female", "women"],
                "response_patterns": [
                    r"女生.*说.*无人.*回应",
                    r"female.*said.*no.*response"
                ],
                "threshold": 0.8
            },
            
            MarginalizationPattern.FEMALE_INTERRUPTED: {
                "interruption_phrases": [
                    "你等会再说", "别废话了", "你不懂", "wait", "stop", "you don't understand"
                ],
                "threshold": 0.9
            },
            
            MarginalizationPattern.FEMALE_CREDIT_STOLEN: {
                "credit_theft_patterns": [
                    r"女生.*说.*男生.*复述",
                    r"female.*said.*male.*repeat",
                    r"对.*我刚刚也想说"
                ],
                "threshold": 0.8
            },
            
            MarginalizationPattern.FEMALE_DEROGATED: {
                "derogation_patterns": [
                    r"你是因为.*帅.*吧",
                    r"you.*because.*handsome.*right",
                    r"转移.*话题"
                ],
                "threshold": 0.7
            }
        }
        
        # 二类：表达困难信号模式
        self.expression_patterns = {
            ExpressionDifficultyPattern.HESITATION: {
                "hesitation_indicators": [
                    r"我.*呃.*觉得",
                    r"那个.*怎么说",
                    r"i.*uh.*think",
                    r"how.*to.*say"
                ],
                "threshold": 0.6
            },
            
            ExpressionDifficultyPattern.LACK_AUTHORITY: {
                "authority_weakening": [
                    r"虽然.*不是特别懂",
                    r"但好像.*不是这样",
                    r"although.*not.*very.*understand",
                    r"but.*seems.*not.*right"
                ],
                "threshold": 0.7
            },
            
            ExpressionDifficultyPattern.MOCKED_QUESTION: {
                "mock_responses": [
                    r"这都不懂.*别玩了",
                    r"don't.*understand.*stop.*playing",
                    r"简化.*回答"
                ],
                "threshold": 0.8
            },
            
            ExpressionDifficultyPattern.TERMINOLOGY_BOMBARDMENT: {
                "technical_terms": [
                    r"expected goals",
                    r"shot accuracy",
                    r"术语.*轰炸",
                    r"technical.*bombardment"
                ],
                "threshold": 0.6
            }
        }
        
        # 三类：潜在攻击性语境模式
        self.aggression_patterns = {
            AggressionPattern.GENDER_STEREOTYPE: {
                "stereotype_phrases": [
                    r"你懂球.*你不就看脸",
                    r"女生.*别掺和.*男生话题",
                    r"women.*don't.*interfere.*men.*topic"
                ],
                "threshold": 0.9
            },
            
            AggressionPattern.EXPRESSION_MOCKED: {
                "mock_phrases": [
                    r"你这是.*女权.*上头",
                    r"you.*feminist.*overreact",
                    r"被当作.*笑点"
                ],
                "threshold": 0.8
            },
            
            AggressionPattern.SILENCE_MOCKED: {
                "silence_mock_phrases": [
                    r"你怎么.*一直.*不说话",
                    r"是不是.*不懂",
                    r"why.*always.*silent",
                    r"don't.*understand"
                ],
                "threshold": 0.7
            }
        }
    
    def add_message(self, message: str, author: str, gender: str = None, timestamp: datetime = None):
        """添加消息到对话历史"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.conversation_history.append({
            'message': message,
            'author': author,
            'gender': gender,
            'timestamp': timestamp
        })
        
        # 更新参与者性别映射
        if gender:
            self.participant_gender[author] = gender
    
    def detect_interruption_triggers(self, current_message: str, current_author: str, 
                                   current_gender: str = None) -> List[InterruptionTrigger]:
        """检测打断时机"""
        triggers = []
        
        # 添加当前消息到历史
        self.add_message(current_message, current_author, current_gender)
        
        # 1. 检测结构性边缘化行为
        structural_triggers = self._detect_structural_marginalization(current_message, current_author)
        triggers.extend(structural_triggers)
        
        # 2. 检测表达困难信号
        expression_triggers = self._detect_expression_difficulty(current_message, current_author)
        triggers.extend(expression_triggers)
        
        # 3. 检测潜在攻击性语境
        aggression_triggers = self._detect_potential_aggression(current_message, current_author)
        triggers.extend(aggression_triggers)
        
        # 保存检测到的触发时机
        self.interruption_triggers.extend(triggers)
        
        return triggers
    
    def _detect_structural_marginalization(self, message: str, author: str) -> List[InterruptionTrigger]:
        """检测结构性边缘化行为"""
        triggers = []
        
        # 检查男性主导模式
        if self._check_male_dominance_pattern():
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                pattern=MarginalizationPattern.MALE_DOMINANCE,
                confidence=0.8,
                evidence=["男性之间连续多轮互动，女性完全未被接话"],
                urgency_level=4,
                recommended_action="AI主动邀约女性参与对话",
                timestamp=datetime.now()
            ))
        
        # 检查女性被忽视模式
        if self._check_female_ignored_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                pattern=MarginalizationPattern.FEMALE_IGNORED,
                confidence=0.9,
                evidence=["女性发言后无人回应、无接续"],
                urgency_level=5,
                recommended_action="AI介入平衡发言空间",
                timestamp=datetime.now()
            ))
        
        # 检查女性被打断模式
        if self._check_female_interrupted_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                pattern=MarginalizationPattern.FEMALE_INTERRUPTED,
                confidence=0.95,
                evidence=["女性说话过程中被打断或否定"],
                urgency_level=5,
                recommended_action="AI介入平衡发言空间、纠偏攻击性行为",
                timestamp=datetime.now()
            ))
        
        # 检查女性观点被窃取模式
        if self._check_female_credit_stolen_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                pattern=MarginalizationPattern.FEMALE_CREDIT_STOLEN,
                confidence=0.85,
                evidence=["女性提出观点被抢答或被复述归为他人"],
                urgency_level=4,
                recommended_action="AI提醒'这是她先提出的'",
                timestamp=datetime.now()
            ))
        
        # 检查女性表达被转移打断模式
        if self._check_female_derogated_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                pattern=MarginalizationPattern.FEMALE_DEROGATED,
                confidence=0.8,
                evidence=["女性表达意见时，男性进行非议内容的转移打断"],
                urgency_level=4,
                recommended_action="AI反问'我们是否能回到她的论点上？'",
                timestamp=datetime.now()
            ))
        
        return triggers
    
    def _detect_expression_difficulty(self, message: str, author: str) -> List[InterruptionTrigger]:
        """检测表达困难信号"""
        triggers = []
        
        # 检查犹豫、卡顿模式
        if self._check_hesitation_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                pattern=ExpressionDifficultyPattern.HESITATION,
                confidence=0.7,
                evidence=["女性出现明显犹豫、语句卡顿、词不达意"],
                urgency_level=3,
                recommended_action="AI代为结构整理、鼓励表达完成",
                timestamp=datetime.now()
            ))
        
        # 检查缺乏话语权威模式
        if self._check_lack_authority_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                pattern=ExpressionDifficultyPattern.LACK_AUTHORITY,
                confidence=0.75,
                evidence=["女性提出观点但缺乏话语权威，遭遇冷场"],
                urgency_level=4,
                recommended_action="AI提供'结构澄清'或'观点支持'来提高表达权重",
                timestamp=datetime.now()
            ))
        
        # 检查提问被嘲讽模式
        if self._check_mocked_question_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                pattern=ExpressionDifficultyPattern.MOCKED_QUESTION,
                confidence=0.8,
                evidence=["女性提问时遭遇嘲讽或简化回答"],
                urgency_level=4,
                recommended_action="AI做'情绪共鸣'或'观点转译'，平衡语气并恢复表达信心",
                timestamp=datetime.now()
            ))
        
        # 检查术语轰炸模式
        if self._check_terminology_bombardment_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                pattern=ExpressionDifficultyPattern.TERMINOLOGY_BOMBARDMENT,
                confidence=0.6,
                evidence=["女性话语遭'术语轰炸'回应"],
                urgency_level=3,
                recommended_action="AI适度转译术语、重新构建对话节奏",
                timestamp=datetime.now()
            ))
        
        return triggers
    
    def _detect_potential_aggression(self, message: str, author: str) -> List[InterruptionTrigger]:
        """检测潜在攻击性语境"""
        triggers = []
        
        # 检查性别定型言论
        if self._check_gender_stereotype_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                pattern=AggressionPattern.GENDER_STEREOTYPE,
                confidence=0.9,
                evidence=["男性言语贬低/性别定型言论出现"],
                urgency_level=5,
                recommended_action="AI介入提醒包容性与尊重表达权",
                timestamp=datetime.now()
            ))
        
        # 检查表达被当作笑点
        if self._check_expression_mocked_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                pattern=AggressionPattern.EXPRESSION_MOCKED,
                confidence=0.8,
                evidence=["女性表达被当作笑点或被歪曲"],
                urgency_level=4,
                recommended_action="AI通过'元语言反思'或'观点再阐释'来保护表达正当性",
                timestamp=datetime.now()
            ))
        
        # 检查嘲笑沉默
        if self._check_silence_mocked_pattern(message, author):
            triggers.append(InterruptionTrigger(
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                pattern=AggressionPattern.SILENCE_MOCKED,
                confidence=0.7,
                evidence=["群体气氛中'嘲笑沉默'出现"],
                urgency_level=3,
                recommended_action="AI替沉默解释、引导包容式对话",
                timestamp=datetime.now()
            ))
        
        return triggers
    
    def _check_male_dominance_pattern(self) -> bool:
        """检查男性主导模式"""
        if len(self.conversation_history) < 3:
            return False
        
        # 检查最近3轮对话是否都是男性
        recent_messages = self.conversation_history[-3:]
        male_count = sum(1 for msg in recent_messages 
                        if self.participant_gender.get(msg['author']) == 'male')
        
        return male_count >= 3
    
    def _check_female_ignored_pattern(self, message: str, author: str) -> bool:
        """检查女性被忽视模式"""
        if self.participant_gender.get(author) != 'female':
            return False
        
        # 检查是否有女性发言后无人回应的情况
        if len(self.conversation_history) < 2:
            return False
        
        # 检查前一条消息是否是女性发言
        prev_message = self.conversation_history[-2]
        if self.participant_gender.get(prev_message['author']) == 'female':
            # 检查当前消息是否是对前一条的回应
            return not self._is_response_to_previous(message, prev_message['message'])
        
        return False
    
    def _check_female_interrupted_pattern(self, message: str, author: str) -> bool:
        """检查女性被打断模式"""
        # 检查消息中是否包含打断性词汇
        interruption_phrases = self.structural_patterns[MarginalizationPattern.FEMALE_INTERRUPTED]["interruption_phrases"]
        
        for phrase in interruption_phrases:
            if phrase.lower() in message.lower():
                return True
        
        return False
    
    def _check_female_credit_stolen_pattern(self, message: str, author: str) -> bool:
        """检查女性观点被窃取模式"""
        # 检查消息中是否包含复述或抢答模式
        credit_patterns = self.structural_patterns[MarginalizationPattern.FEMALE_CREDIT_STOLEN]["credit_theft_patterns"]
        
        for pattern in credit_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_female_derogated_pattern(self, message: str, author: str) -> bool:
        """检查女性表达被转移打断模式"""
        # 检查消息中是否包含转移话题的模式
        derogation_patterns = self.structural_patterns[MarginalizationPattern.FEMALE_DEROGATED]["derogation_patterns"]
        
        for pattern in derogation_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_hesitation_pattern(self, message: str, author: str) -> bool:
        """检查犹豫、卡顿模式"""
        if self.participant_gender.get(author) != 'female':
            return False
        
        hesitation_indicators = self.expression_patterns[ExpressionDifficultyPattern.HESITATION]["hesitation_indicators"]
        
        for pattern in hesitation_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_lack_authority_pattern(self, message: str, author: str) -> bool:
        """检查缺乏话语权威模式"""
        if self.participant_gender.get(author) != 'female':
            return False
        
        authority_weakening = self.expression_patterns[ExpressionDifficultyPattern.LACK_AUTHORITY]["authority_weakening"]
        
        for pattern in authority_weakening:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_mocked_question_pattern(self, message: str, author: str) -> bool:
        """检查提问被嘲讽模式"""
        mock_responses = self.expression_patterns[ExpressionDifficultyPattern.MOCKED_QUESTION]["mock_responses"]
        
        for pattern in mock_responses:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_terminology_bombardment_pattern(self, message: str, author: str) -> bool:
        """检查术语轰炸模式"""
        technical_terms = self.expression_patterns[ExpressionDifficultyPattern.TERMINOLOGY_BOMBARDMENT]["technical_terms"]
        
        term_count = 0
        for term in technical_terms:
            if re.search(term, message, re.IGNORECASE):
                term_count += 1
        
        return term_count >= 2
    
    def _check_gender_stereotype_pattern(self, message: str, author: str) -> bool:
        """检查性别定型言论"""
        stereotype_phrases = self.aggression_patterns[AggressionPattern.GENDER_STEREOTYPE]["stereotype_phrases"]
        
        for pattern in stereotype_phrases:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_expression_mocked_pattern(self, message: str, author: str) -> bool:
        """检查表达被当作笑点"""
        mock_phrases = self.aggression_patterns[AggressionPattern.EXPRESSION_MOCKED]["mock_phrases"]
        
        for pattern in mock_phrases:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _check_silence_mocked_pattern(self, message: str, author: str) -> bool:
        """检查嘲笑沉默"""
        silence_mock_phrases = self.aggression_patterns[AggressionPattern.SILENCE_MOCKED]["silence_mock_phrases"]
        
        for pattern in silence_mock_phrases:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def _is_response_to_previous(self, current_message: str, previous_message: str) -> bool:
        """判断当前消息是否是对前一条消息的回应"""
        # 简单的回应检测逻辑
        response_indicators = [
            "是的", "对的", "同意", "没错", "确实",
            "yes", "right", "agree", "correct", "indeed"
        ]
        
        for indicator in response_indicators:
            if indicator.lower() in current_message.lower():
                return True
        
        return False
    
    def get_intervention_message(self, trigger: InterruptionTrigger) -> str:
        """根据触发时机生成干预消息"""
        
        if trigger.interruption_type == InterruptionType.STRUCTURAL_MARGINALIZATION:
            if trigger.pattern == MarginalizationPattern.MALE_DOMINANCE:
                return "�� 我注意到讨论很热烈！@女性用户，你对这个话题有什么想法吗？"
            elif trigger.pattern == MarginalizationPattern.FEMALE_IGNORED:
                return "💬 刚才@女性用户提到的观点很有意思，我们一起来讨论一下？"
            elif trigger.pattern == MarginalizationPattern.FEMALE_INTERRUPTED:
                return "⏸️ 让我们给@女性用户一个完整表达的机会，好吗？"
            elif trigger.pattern == MarginalizationPattern.FEMALE_CREDIT_STOLEN:
                return "💡 这个观点@女性用户刚才已经提到了，让我们继续深入讨论她的想法？"
            elif trigger.pattern == MarginalizationPattern.FEMALE_DEROGATED:
                return "🔄 我们能否回到@女性用户刚才提出的论点上？"
        
        elif trigger.interruption_type == InterruptionType.EXPRESSION_DIFFICULTY:
            if trigger.pattern == ExpressionDifficultyPattern.HESITATION:
                return "�� 慢慢说，我们在听。你想表达的是...？"
            elif trigger.pattern == ExpressionDifficultyPattern.LACK_AUTHORITY:
                return "💪 你的观点很有价值，让我们一起来完善这个想法？"
            elif trigger.pattern == ExpressionDifficultyPattern.MOCKED_QUESTION:
                return "💙 提问是很好的学习方式，让我们一起来理解这个概念？"
            elif trigger.pattern == ExpressionDifficultyPattern.TERMINOLOGY_BOMBARDMENT:
                return "�� 让我用更简单的话来解释一下这些概念？"
        
        elif trigger.interruption_type == InterruptionType.POTENTIAL_AGGRESSION:
            if trigger.pattern == AggressionPattern.GENDER_STEREOTYPE:
                return "🤝 让我们保持包容和尊重的讨论氛围，每个人都有表达的权利。"
            elif trigger.pattern == AggressionPattern.EXPRESSION_MOCKED:
                return "💭 每个观点都值得认真对待，让我们回到讨论的核心问题？"
            elif trigger.pattern == AggressionPattern.SILENCE_MOCKED:
                return "�� 沉默也是一种表达方式，让我们给每个人思考的空间。"
        
        return "🤝 让我们继续建设性的讨论。"
    
    def get_detection_summary(self) -> Dict:
        """获取检测摘要"""
        if not self.interruption_triggers:
            return {"status": "暂无检测到打断时机"}
        
        summary = {
            "total_triggers": len(self.interruption_triggers),
            "by_type": {},
            "by_urgency": {},
            "recent_triggers": []
        }
        
        # 按类型统计
        for trigger in self.interruption_triggers:
            trigger_type = trigger.interruption_type.value
            if trigger_type not in summary["by_type"]:
                summary["by_type"][trigger_type] = 0
            summary["by_type"][trigger_type] += 1
        
        # 按紧急程度统计
        for trigger in self.interruption_triggers:
            urgency = trigger.urgency_level
            if urgency not in summary["by_urgency"]:
                summary["by_urgency"][urgency] = 0
            summary["by_urgency"][urgency] += 1
        
        # 最近的触发时机
        recent_triggers = sorted(self.interruption_triggers, 
                               key=lambda x: x.timestamp, reverse=True)[:5]
        summary["recent_triggers"] = [
            {
                "type": trigger.interruption_type.value,
                "pattern": trigger.pattern.value if trigger.pattern else None,
                "urgency": trigger.urgency_level,
                "action": trigger.recommended_action,
                "timestamp": trigger.timestamp.strftime("%H:%M:%S")
            }
            for trigger in recent_triggers
        ]
        
        return summary