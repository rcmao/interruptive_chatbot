"""
纯上下文对话流冲突检测系统
从第三轮对话开始，基于对话模式和TKI策略分析
"""

import asyncio
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)

class DialoguePhase(Enum):
    """对话阶段"""
    OPENING = "opening"           # 开场阶段 (1-2轮)
    DEVELOPMENT = "development"   # 发展阶段 (3-5轮)
    ESCALATION = "escalation"     # 升级阶段 (6+轮)
    RESOLUTION = "resolution"     # 解决阶段

class ConflictPattern(Enum):
    """冲突模式类型"""
    BLAME_CYCLE = "blame_cycle"           # 相互指责循环
    ISSUE_REPETITION = "issue_repetition" # 问题重复提及
    DEFENSIVE_SPIRAL = "defensive_spiral" # 防御性螺旋上升
    POWER_STRUGGLE = "power_struggle"     # 权力争夺
    TASK_CONFLICT = "task_conflict"       # 任务冲突
    
class TKIStrategy(Enum):
    """TKI干预策略"""
    COLLABORATING = "collaborating"    # 协作：寻求双赢
    ACCOMMODATING = "accommodating"    # 迁就：优先关系
    COMPETING = "competing"            # 竞争：坚持立场  
    AVOIDING = "avoiding"              # 回避：暂停冲突
    COMPROMISING = "compromising"      # 妥协：互相让步

@dataclass
class ConversationTurn:
    """单轮对话"""
    speaker: str
    content: str
    timestamp: datetime
    turn_number: int
    response_to: Optional[str] = None  # 回应的是谁

@dataclass
class ContextAnalysis:
    """上下文分析结果"""
    conflict_score: float           # 0-1 冲突强度
    pattern_detected: Optional[ConflictPattern]
    recommended_strategy: TKIStrategy
    intervention_message: str
    analysis_reasoning: str
    should_intervene: bool

class ConversationFlowAnalyzer:
    """对话流分析器"""
    
    def __init__(self, min_turns_for_analysis: int = 3):
        self.conversation_history = deque(maxlen=20)
        self.participant_states = {}
        self.min_turns = min_turns_for_analysis
        
    def add_turn(self, speaker: str, content: str) -> Optional[ContextAnalysis]:
        """添加对话轮次并分析"""
        turn = ConversationTurn(
            speaker=speaker,
            content=content,
            timestamp=datetime.now(),
            turn_number=len(self.conversation_history) + 1
        )
        
        self.conversation_history.append(turn)
        self._update_participant_state(speaker, content)
        
        # 从第三轮开始分析
        if len(self.conversation_history) >= self.min_turns:
            return self._analyze_conversation_flow()
        
        return ContextAnalysis(
            conflict_score=0.0,
            pattern_detected=None,
            recommended_strategy=TKIStrategy.COLLABORATING,
            intervention_message="",
            analysis_reasoning="对话轮次不足，继续观察",
            should_intervene=False
        )
    
    def _update_participant_state(self, speaker: str, content: str):
        """更新参与者状态"""
        if speaker not in self.participant_states:
            self.participant_states[speaker] = {
                'turn_count': 0,
                'recent_topics': [],
                'emotional_trajectory': [],
                'response_patterns': []
            }
        
        state = self.participant_states[speaker]
        state['turn_count'] += 1
        state['recent_topics'].append(content[:50])  # 保存话题摘要
        
        # 简单情绪评估
        emotion_score = self._assess_emotional_tone(content)
        state['emotional_trajectory'].append(emotion_score)
        
        # 保持最近5次记录
        for key in ['recent_topics', 'emotional_trajectory']:
            if len(state[key]) > 5:
                state[key] = state[key][-5:]
    
    def _assess_emotional_tone(self, content: str) -> float:
        """评估情绪色调 (0=消极, 0.5=中性, 1=积极)"""
        # 基于语气和表达方式的简单评估
        indicators = {
            'negative': ['但', '可是', '然而', '不过', '问题是', '你', '没有'],
            'neutral': ['我们', '大家', '一起', '讨论', '看看'],
            'positive': ['好', '可以', '没问题', '赞同', '支持']
        }
        
        content_lower = content.lower()
        negative_count = sum(1 for word in indicators['negative'] if word in content_lower)
        positive_count = sum(1 for word in indicators['positive'] if word in content_lower)
        
        if negative_count > positive_count:
            return max(0.0, 0.5 - (negative_count * 0.1))
        elif positive_count > negative_count:
            return min(1.0, 0.5 + (positive_count * 0.1))
        else:
            return 0.5
    
    def _analyze_conversation_flow(self) -> ContextAnalysis:
        """分析对话流模式"""
        recent_turns = list(self.conversation_history)[-5:]  # 分析最近5轮
        
        # 1. 检测冲突模式
        pattern = self._detect_conflict_pattern(recent_turns)
        
        # 2. 计算冲突强度
        conflict_score = self._calculate_conflict_intensity(recent_turns, pattern)
        
        # 3. 选择TKI策略
        strategy = self._select_tki_strategy(pattern, conflict_score, recent_turns)
        
        # 4. 生成干预消息
        intervention_msg = self._generate_intervention(strategy, pattern, recent_turns)
        
        # 5. 决定是否干预
        should_intervene = conflict_score > 0.4  # 阈值设为0.4
        
        # 6. 生成分析说明
        reasoning = self._generate_analysis_reasoning(pattern, conflict_score, recent_turns)
        
        return ContextAnalysis(
            conflict_score=conflict_score,
            pattern_detected=pattern,
            recommended_strategy=strategy,
            intervention_message=intervention_msg,
            analysis_reasoning=reasoning,
            should_intervene=should_intervene
        )
    
    def _detect_conflict_pattern(self, turns: List[ConversationTurn]) -> Optional[ConflictPattern]:
        """检测冲突模式"""
        if len(turns) < 3:
            return None
        
        speakers = [turn.speaker for turn in turns]
        contents = [turn.content for turn in turns]
        
        # 检测相互指责循环
        if self._is_blame_cycle(turns):
            return ConflictPattern.BLAME_CYCLE
        
        # 检测问题重复
        if self._is_issue_repetition(contents):
            return ConflictPattern.ISSUE_REPETITION
        
        # 检测防御性螺旋
        if self._is_defensive_spiral(turns):
            return ConflictPattern.DEFENSIVE_SPIRAL
        
        # 检测任务冲突
        if self._is_task_conflict(contents):
            return ConflictPattern.TASK_CONFLICT
        
        return None
    
    def _is_blame_cycle(self, turns: List[ConversationTurn]) -> bool:
        """检测相互指责循环"""
        if len(turns) < 3:
            return False
        
        # 检查是否有来回指责
        blame_indicators = 0
        for i in range(len(turns) - 1):
            current_content = turns[i].content
            next_content = turns[i + 1].content
            
            # 简单检测：一方提出问题，另一方反驳
            if ('你' in current_content and len(current_content) > 10) and \
               ('但' in next_content or '可是' in next_content or '我觉得' in next_content):
                blame_indicators += 1
        
        return blame_indicators >= 2
    
    def _is_issue_repetition(self, contents: List[str]) -> bool:
        """检测问题重复"""
        # 检查是否有相似的表达重复出现
        for i, content1 in enumerate(contents):
            for j, content2 in enumerate(contents[i+1:], i+1):
                if self._content_similarity(content1, content2) > 0.6:
                    return True
        return False
    
    def _content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度"""
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _is_defensive_spiral(self, turns: List[ConversationTurn]) -> bool:
        """检测防御性螺旋"""
        defensive_indicators = ['我觉得', '我认为', '不是我', '但是', '可是']
        
        defensive_count = 0
        for turn in turns[-3:]:  # 检查最近3轮
            if any(indicator in turn.content for indicator in defensive_indicators):
                defensive_count += 1
        
        return defensive_count >= 2
    
    def _is_task_conflict(self, contents: List[str]) -> bool:
        """检测任务冲突"""
        task_indicators = ['ppt', '内容', '讲', '排练', '时间', '按照', '方式', '方法']
        
        task_mentions = 0
        for content in contents:
            if any(indicator in content.lower() for indicator in task_indicators):
                task_mentions += 1
        
        return task_mentions >= 2
    
    def _calculate_conflict_intensity(self, turns: List[ConversationTurn], pattern: Optional[ConflictPattern]) -> float:
        """计算冲突强度"""
        base_score = 0.0
        
        # 基于情绪轨迹
        emotions = []
        for speaker in self.participant_states:
            emotions.extend(self.participant_states[speaker]['emotional_trajectory'][-3:])
        
        if emotions:
            avg_emotion = sum(emotions) / len(emotions)
            # 情绪偏离中性程度
            emotion_deviation = abs(avg_emotion - 0.5) * 2
            base_score += emotion_deviation * 0.4
        
        # 基于对话长度和复杂度
        avg_length = sum(len(turn.content) for turn in turns) / len(turns)
        if avg_length > 30:  # 长句子通常表示更复杂的表达
            base_score += 0.2
        
        # 基于模式类型
        pattern_weights = {
            ConflictPattern.BLAME_CYCLE: 0.4,
            ConflictPattern.ISSUE_REPETITION: 0.3,
            ConflictPattern.DEFENSIVE_SPIRAL: 0.3,
            ConflictPattern.TASK_CONFLICT: 0.2,
            ConflictPattern.POWER_STRUGGLE: 0.5
        }
        
        if pattern:
            base_score += pattern_weights.get(pattern, 0.2)
        
        # 基于参与者数量和轮次
        if len(self.participant_states) > 1 and len(turns) > 4:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _select_tki_strategy(self, pattern: Optional[ConflictPattern], 
                           intensity: float, turns: List[ConversationTurn]) -> TKIStrategy:
        """选择TKI策略"""
        
        # 基于冲突模式选择策略
        if pattern == ConflictPattern.BLAME_CYCLE:
            return TKIStrategy.ACCOMMODATING  # 优先缓解情绪
        elif pattern == ConflictPattern.ISSUE_REPETITION:
            return TKIStrategy.COLLABORATING  # 寻求解决方案
        elif pattern == ConflictPattern.DEFENSIVE_SPIRAL:
            return TKIStrategy.AVOIDING       # 暂停升级
        elif pattern == ConflictPattern.TASK_CONFLICT:
            return TKIStrategy.COMPROMISING   # 寻求中间方案
        elif pattern == ConflictPattern.POWER_STRUGGLE:
            return TKIStrategy.COMPETING      # 明确边界
        
        # 基于强度选择
        if intensity > 0.7:
            return TKIStrategy.AVOIDING       # 高强度时先降温
        elif intensity > 0.5:
            return TKIStrategy.ACCOMMODATING  # 中等强度时缓解
        else:
            return TKIStrategy.COLLABORATING  # 低强度时协作
    
    def _generate_intervention(self, strategy: TKIStrategy, pattern: Optional[ConflictPattern], 
                              turns: List[ConversationTurn]) -> str:
        """生成干预消息"""
        
        intervention_templates = {
            TKIStrategy.COLLABORATING: [
                "我注意到大家都有很好的想法。也许我们可以一起找个解决方案？ 🤝",
                "看起来我们都希望把事情做好。让我们集思广益，看看怎么改进？ 💡"
            ],
            TKIStrategy.ACCOMMODATING: [
                "我能理解大家的感受。也许我们先放松一下，重新整理思路？ 😊",
                "每个人的观点都很重要。让我们给彼此一些理解的空间。 💙"
            ],
            TKIStrategy.AVOIDING: [
                "大家似乎需要一些时间思考。不如我们休息5分钟再继续？ ⏸️",
                "让我们暂停一下，重新审视这个问题的核心。 🔄"
            ],
            TKIStrategy.COMPROMISING: [
                "看起来我们都有合理的观点。有没有可能找到一个平衡方案？ ⚖️",
                "也许我们可以各退一步，寻找一个大家都能接受的解决方案？ 🤝"
            ],
            TKIStrategy.COMPETING: [
                "我们需要明确目标和责任。让我们专注于最重要的事情。 🎯",
                "时间有限，让我们决定一个明确的行动方案。 ⚡"
            ]
        }
        
        templates = intervention_templates.get(strategy, intervention_templates[TKIStrategy.COLLABORATING])
        
        # 根据模式选择更具体的模板
        if pattern == ConflictPattern.TASK_CONFLICT:
            return "我注意到大家对执行方式有不同看法。也许我们可以明确一下各自的职责和期望？ 📋"
        elif pattern == ConflictPattern.BLAME_CYCLE:
            return "我感觉到一些紧张。让我们把注意力放回到解决问题上，而不是谁对谁错。 🔧"
        
        # 返回默认模板
        return templates[0]
    
    def _generate_analysis_reasoning(self, pattern: Optional[ConflictPattern], 
                                   intensity: float, turns: List[ConversationTurn]) -> str:
        """生成分析推理"""
        reasoning_parts = []
        
        reasoning_parts.append(f"对话轮次: {len(self.conversation_history)}")
        reasoning_parts.append(f"冲突强度: {intensity:.2f}")
        
        if pattern:
            reasoning_parts.append(f"检测到模式: {pattern.value}")
        
        # 参与者分析
        active_speakers = len(self.participant_states)
        reasoning_parts.append(f"活跃参与者: {active_speakers}人")
        
        # 情绪趋势
        recent_emotions = []
        for state in self.participant_states.values():
            if state['emotional_trajectory']:
                recent_emotions.extend(state['emotional_trajectory'][-2:])
        
        if recent_emotions:
            avg_emotion = sum(recent_emotions) / len(recent_emotions)
            emotion_trend = "消极" if avg_emotion < 0.4 else "积极" if avg_emotion > 0.6 else "中性"
            reasoning_parts.append(f"情绪趋势: {emotion_trend}")
        
        return "; ".join(reasoning_parts)

# 集成到主系统
class ContextBasedConflictBot:
    """基于上下文的冲突检测机器人"""
    
    def __init__(self):
        self.analyzer = ConversationFlowAnalyzer(min_turns_for_analysis=3)
        self.analysis_history = deque(maxlen=50)
        
    async def process_message(self, message: str, author: str) -> Optional[str]:
        """处理消息"""
        # 分析对话流
        analysis = self.analyzer.add_turn(author, message)
        
        # 记录分析历史
        if analysis:
            analysis_record = {
                'timestamp': datetime.now(),
                'author': author,
                'message': message[:50] + "..." if len(message) > 50 else message,
                'conflict_score': analysis.conflict_score,
                'pattern': analysis.pattern_detected.value if analysis.pattern_detected else None,
                'strategy': analysis.recommended_strategy.value,
                'should_intervene': analysis.should_intervene,
                'reasoning': analysis.analysis_reasoning,
                'intervention': analysis.intervention_message if analysis.should_intervene else None
            }
            
            self.analysis_history.append(analysis_record)
            
            # 打印监控信息
            self._print_analysis(analysis_record)
            
            # 返回干预消息
            if analysis.should_intervene:
                return analysis.intervention_message
        
        return None
    
    def _print_analysis(self, record: Dict):
        """打印分析结果"""
        timestamp = record['timestamp'].strftime('%H:%M:%S')
        status = "🚨" if record['should_intervene'] else "✅"
        
        score_bar = "█" * int(record['conflict_score'] * 10) + "░" * (10 - int(record['conflict_score'] * 10))
        
        print(f"""
{status} [{timestamp}] {record['author']} (轮次#{len(self.analysis_history)})
📝 {record['message']}
📊 冲突强度: {record['conflict_score']:.2f} {score_bar}
🎯 检测模式: {record['pattern'] or '无'}
🛠️  推荐策略: {record['strategy']}
💭 分析依据: {record['reasoning']}
        """.strip())
        
        if record['should_intervene']:
            print(f"💬 干预建议: {record['intervention']}")
        
        print("─" * 70)

# 测试函数
async def test_context_based_detection():
    """测试基于上下文的检测"""
    
    bot = ContextBasedConflictBot()
    
    # 测试对话序列
    conversation = [
        ("Ruochen Mao", "我们今天排练第三次了，你能不能这次按PPT内容来讲？"),
        ("小明", "昨天老师点名我们超时了……"),
        ("Ruochen Mao", "但那是因为你讲太久，我临场讲两句就顺带收尾了。"),
        ("小明", "我觉得讲稿念出来太死板了。"),
        ("Ruochen Mao", "可是我们需要控制时间啊，不然又要被老师批评"),
        ("小明", "那你觉得应该怎么办？")
    ]
    
    print("🔍 开始基于上下文的冲突检测测试...")
    print("=" * 70)
    
    for author, message in conversation:
        intervention = await bot.process_message(message, author)
        
        if intervention:
            print(f"🤖 机器人干预: {intervention}")
            print("─" * 70)
        
        # 模拟对话间隔
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_context_based_detection()) 