"""
上下文感知的冲突检测系统
基于对话历史和情绪轨迹的渐进式冲突检测
"""

import asyncio
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ConflictPattern(Enum):
    """冲突模式类型"""
    ESCALATING = "escalating"           # 逐步升级
    REPEATING_CONCERNS = "repeating"    # 重复担忧
    RESPONSIBILITY_SHIFT = "shifting"   # 责任推卸
    DEADLINE_PRESSURE = "deadline"      # 截止日期压力
    GROUP_DYNAMICS = "group"           # 群体动力学

@dataclass
class ContextualAnalysis:
    """上下文分析结果"""
    current_score: float
    trend_score: float
    pattern_detected: Optional[ConflictPattern]
    escalation_level: int  # 1-5级
    intervention_urgency: float
    evidence_summary: str
    recommendation: str

class ConversationTracker:
    """对话追踪器"""
    
    def __init__(self, window_size: int = 5):
        self.message_history = deque(maxlen=20)
        self.score_history = deque(maxlen=15)
        self.pattern_history = deque(maxlen=10)
        self.participant_states = {}
        self.conversation_start = datetime.now()
        self.window_size = window_size
        
    def add_message(self, message: str, author: str, score: float, analysis: dict):
        """添加消息和分析结果"""
        timestamp = datetime.now()
        
        message_data = {
            'content': message,
            'author': author, 
            'timestamp': timestamp,
            'score': score,
            'analysis': analysis
        }
        
        self.message_history.append(message_data)
        self.score_history.append(score)
        
        # 更新参与者状态
        if author not in self.participant_states:
            self.participant_states[author] = {
                'message_count': 0,
                'avg_score': 0.0,
                'last_active': timestamp,
                'escalation_count': 0
            }
        
        state = self.participant_states[author]
        state['message_count'] += 1
        state['avg_score'] = (state['avg_score'] * (state['message_count'] - 1) + score) / state['message_count']
        state['last_active'] = timestamp
        
        # 检测个人升级模式
        if score > 0.5 and len(self.score_history) >= 2:
            if self.score_history[-2] < self.score_history[-1]:
                state['escalation_count'] += 1
    
    def analyze_context(self) -> ContextualAnalysis:
        """分析上下文"""
        if len(self.message_history) < 2:
            return ContextualAnalysis(
                current_score=0.0,
                trend_score=0.0,
                pattern_detected=None,
                escalation_level=1,
                intervention_urgency=0.0,
                evidence_summary="消息数量不足",
                recommendation="继续观察"
            )
        
        # 1. 当前分数（最近消息的平均）
        recent_scores = list(self.score_history)[-self.window_size:]
        current_score = sum(recent_scores) / len(recent_scores)
        
        # 2. 趋势分析
        trend_score = self._calculate_trend()
        
        # 3. 模式检测
        pattern_detected = self._detect_patterns()
        
        # 4. 升级等级评估
        escalation_level = self._assess_escalation_level(current_score, trend_score, pattern_detected)
        
        # 5. 干预紧急程度
        intervention_urgency = self._calculate_intervention_urgency(
            current_score, trend_score, escalation_level, pattern_detected
        )
        
        # 6. 证据总结
        evidence_summary = self._generate_evidence_summary(pattern_detected, trend_score)
        
        # 7. 建议
        recommendation = self._generate_recommendation(intervention_urgency, escalation_level)
        
        return ContextualAnalysis(
            current_score=current_score,
            trend_score=trend_score,
            pattern_detected=pattern_detected,
            escalation_level=escalation_level,
            intervention_urgency=intervention_urgency,
            evidence_summary=evidence_summary,
            recommendation=recommendation
        )
    
    def _calculate_trend(self) -> float:
        """计算趋势分数"""
        if len(self.score_history) < 3:
            return 0.0
        
        scores = list(self.score_history)
        
        # 线性回归计算趋势
        n = len(scores)
        x = list(range(n))
        y = scores
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # 归一化斜率到0-1范围
        return max(0, min(1, slope * 5))  # 乘以5来放大趋势信号
    
    def _detect_patterns(self) -> Optional[ConflictPattern]:
        """检测冲突模式"""
        messages = list(self.message_history)[-5:]  # 检查最近5条消息
        
        if len(messages) < 3:
            return None
        
        # 检测升级模式
        scores = [msg['score'] for msg in messages]
        if len(scores) >= 3 and scores[-1] > scores[-2] > scores[-3]:
            return ConflictPattern.ESCALATING
        
        # 检测重复关切
        contents = [msg['content'].lower() for msg in messages]
        keywords = ['什么时候', '还没', '还要', '到底', '能不能']
        repeated_concerns = sum(1 for content in contents for kw in keywords if kw in content)
        if repeated_concerns >= 2:
            return ConflictPattern.REPEATING_CONCERNS
        
        # 检测截止日期压力
        deadline_keywords = ['天', '交', 'ddl', '截止', '时间', '急']
        deadline_mentions = sum(1 for content in contents for kw in deadline_keywords if kw in content)
        if deadline_mentions >= 2:
            return ConflictPattern.DEADLINE_PRESSURE
        
        # 检测责任推卸
        blame_keywords = ['你', '没有', '不', '为什么']
        blame_count = sum(1 for content in contents for kw in blame_keywords if kw in content)
        if blame_count >= 3:
            return ConflictPattern.RESPONSIBILITY_SHIFT
        
        return None
    
    def _assess_escalation_level(self, current_score: float, trend_score: float, pattern: Optional[ConflictPattern]) -> int:
        """评估升级等级 (1-5)"""
        base_level = 1
        
        # 基于当前分数
        if current_score > 0.7:
            base_level = 4
        elif current_score > 0.5:
            base_level = 3
        elif current_score > 0.3:
            base_level = 2
        
        # 趋势调整
        if trend_score > 0.3:
            base_level += 1
        
        # 模式调整
        if pattern == ConflictPattern.ESCALATING:
            base_level += 1
        elif pattern == ConflictPattern.DEADLINE_PRESSURE:
            base_level += 1
        
        return min(5, max(1, base_level))
    
    def _calculate_intervention_urgency(self, current_score: float, trend_score: float, 
                                       escalation_level: int, pattern: Optional[ConflictPattern]) -> float:
        """计算干预紧急程度"""
        urgency = current_score * 0.4 + trend_score * 0.4
        
        # 升级等级调整
        urgency += (escalation_level - 1) * 0.1
        
        # 模式调整
        if pattern == ConflictPattern.ESCALATING:
            urgency += 0.2
        elif pattern == ConflictPattern.DEADLINE_PRESSURE:
            urgency += 0.15
        
        return min(1.0, urgency)
    
    def _generate_evidence_summary(self, pattern: Optional[ConflictPattern], trend: float) -> str:
        """生成证据总结"""
        evidence = []
        
        if pattern:
            evidence.append(f"检测到{pattern.value}模式")
        
        if trend > 0.3:
            evidence.append(f"情绪呈上升趋势({trend:.2f})")
        
        if len(self.participant_states) > 1:
            active_participants = sum(1 for state in self.participant_states.values() 
                                    if state['avg_score'] > 0.3)
            if active_participants > 1:
                evidence.append(f"{active_participants}人情绪异常")
        
        return "; ".join(evidence) if evidence else "暂无明显冲突信号"
    
    def _generate_recommendation(self, urgency: float, escalation_level: int) -> str:
        """生成建议"""
        if urgency > 0.7:
            return "🚨 立即干预 - 冲突风险很高"
        elif urgency > 0.5:
            return "⚠️ 建议干预 - 情况正在恶化"
        elif urgency > 0.3:
            return "👀 密切关注 - 有潜在风险"
        else:
            return "✅ 继续观察 - 情况正常"

class ContextAwareBot:
    """上下文感知机器人"""
    
    def __init__(self):
        self.tracker = ConversationTracker()
        self.analysis_history = deque(maxlen=50)
    
    async def analyze_message_with_context(self, message: str, author: str) -> Dict:
        """带上下文的消息分析"""
        
        # 1. 单句分析（现有逻辑）
        from core.explainable_system import ExplainableInterventionBot
        single_bot = ExplainableInterventionBot()
        single_result = await single_bot.process_message_with_explanation(message, author, "context")
        
        # 提取单句分数
        single_score = 0.5 if single_result else 0.2  # 简化提取逻辑
        
        # 2. 添加到上下文追踪
        self.tracker.add_message(message, author, single_score, {'single_result': single_result})
        
        # 3. 上下文分析
        context_analysis = self.tracker.analyze_context()
        
        # 4. 综合决策
        should_intervene = context_analysis.intervention_urgency > 0.5
        intervention_message = None
        
        if should_intervene:
            intervention_message = self._generate_contextual_intervention(context_analysis, message, author)
        
        # 5. 保存分析历史
        analysis_record = {
            'timestamp': datetime.now(),
            'message': message[:50] + "..." if len(message) > 50 else message,
            'author': author,
            'single_score': single_score,
            'context_score': context_analysis.current_score,
            'trend_score': context_analysis.trend_score,
            'escalation_level': context_analysis.escalation_level,
            'urgency': context_analysis.intervention_urgency,
            'pattern': context_analysis.pattern_detected.value if context_analysis.pattern_detected else None,
            'should_intervene': should_intervene,
            'intervention': intervention_message
        }
        
        self.analysis_history.append(analysis_record)
        
        return {
            'should_intervene': should_intervene,
            'intervention_message': intervention_message,
            'context_analysis': context_analysis,
            'single_score': single_score,
            'analysis_record': analysis_record
        }
    
    def _generate_contextual_intervention(self, analysis: ContextualAnalysis, message: str, author: str) -> str:
        """生成上下文相关的干预"""
        
        if analysis.pattern_detected == ConflictPattern.DEADLINE_PRESSURE:
            return "我注意到大家对截止时间很担心。让我们一起看看如何合理安排剩余时间？ 🕒"
        
        elif analysis.pattern_detected == ConflictPattern.REPEATING_CONCERNS:
            return "我看到同样的担忧被提到了几次。也许我们可以直接讨论解决方案？ 💡"
        
        elif analysis.pattern_detected == ConflictPattern.ESCALATING:
            return "对话情绪似乎在升级。让我们暂停一下，重新整理思路？ 🤝"
        
        elif analysis.escalation_level >= 4:
            return "我感觉到一些紧张。也许我们可以从不同角度来看这个问题？ 🔄"
        
        else:
            return "我注意到一些沟通上的挑战。大家有什么想法可以分享吗？ 💬"
    
    def get_monitoring_dashboard(self) -> Dict:
        """获取监控仪表板数据"""
        
        if not self.analysis_history:
            return {'status': '暂无数据'}
        
        recent_analyses = list(self.analysis_history)[-10:]
        
        return {
            'current_status': {
                'last_analysis': recent_analyses[-1],
                'trend': 'increasing' if len(recent_analyses) >= 2 and recent_analyses[-1]['urgency'] > recent_analyses[-2]['urgency'] else 'stable',
                'active_participants': len(self.tracker.participant_states),
                'conversation_duration': str(datetime.now() - self.tracker.conversation_start).split('.')[0]
            },
            'score_timeline': [
                {
                    'timestamp': analysis['timestamp'].strftime('%H:%M:%S'),
                    'single_score': analysis['single_score'],
                    'context_score': analysis['context_score'],
                    'urgency': analysis['urgency']
                }
                for analysis in recent_analyses
            ],
            'recent_messages': [
                {
                    'time': analysis['timestamp'].strftime('%H:%M:%S'),
                    'author': analysis['author'],
                    'message': analysis['message'],
                    'scores': {
                        'single': f"{analysis['single_score']:.2f}",
                        'context': f"{analysis['context_score']:.2f}",
                        'urgency': f"{analysis['urgency']:.2f}"
                    },
                    'level': analysis['escalation_level'],
                    'pattern': analysis['pattern'],
                    'intervened': '🚨' if analysis['should_intervene'] else '✅'
                }
                for analysis in recent_analyses
            ],
            'statistics': {
                'total_messages': len(self.analysis_history),
                'interventions': sum(1 for a in self.analysis_history if a['should_intervene']),
                'avg_urgency': sum(a['urgency'] for a in recent_analyses) / len(recent_analyses),
                'max_escalation': max(a['escalation_level'] for a in recent_analyses)
            }
        }

# 使用示例和测试
async def test_context_aware_detection():
    """测试上下文感知检测"""
    
    bot = ContextAwareBot()
    
    # 模拟对话序列（来自示例）
    conversation = [
        ("Ruochen Mao", "hi，睡了吗？现在方便聊下海报的事情吗？"),
        ("其他人", "在的，我刚写完另一门作业，咋了"),
        ("Ruochen Mao", "就是我们那个海报还有4天就要交了，我这边内容都排好了，但你那边的主图还没收到......"),
        ("Ruochen Mao", "我昨天问过你一次，可能你太忙了没看见？"),
        ("Ruochen Mao", "......啊不好意思，我看到了忘回了。我想着等着画的差不多了再跟你说"),
        ("Ruochen Mao", "最近状态不太好，画图那边一直没啥灵感"),
        ("Ruochen Mao", "嗯嗯好的，就是主要这个是个作业有明确的ddl,不是灵不灵感的问题......"),
        ("Ruochen Mao", "我们就俩人，我这边做了三版了，然后你那边就给你安排了个小任务，可能一下午就做完了吧"),
        ("Ruochen Mao", "你那边能明确下时间什么时候给我吗"),
        ("Ruochen Mao", "还是你就不想做了？"),
        ("Ruochen Mao", "我不是想让你一个人做啦")
    ]
    
    print("🔍 开始上下文感知测试...")
    print("=" * 60)
    
    for i, (author, message) in enumerate(conversation):
        print(f"\n📨 消息 {i+1} - {author}")
        print(f"内容: {message}")
        
        result = await bot.analyze_message_with_context(message, author)
        
        analysis = result['context_analysis']
        record = result['analysis_record']
        
        print(f"📊 分析结果:")
        print(f"   单句分数: {record['single_score']:.3f}")
        print(f"   上下文分数: {record['context_score']:.3f}")
        print(f"   趋势分数: {record['trend_score']:.3f}")
        print(f"   升级等级: {analysis.escalation_level}/5")
        print(f"   干预紧急度: {record['urgency']:.3f}")
        print(f"   检测模式: {record['pattern'] or '无'}")
        print(f"   建议: {analysis.recommendation}")
        
        if result['should_intervene']:
            print(f"🚨 干预建议: {result['intervention_message']}")
        
        print("-" * 40)
    
    # 显示监控仪表板
    dashboard = bot.get_monitoring_dashboard()
    print(f"\n📊 监控仪表板:")
    print(f"对话时长: {dashboard['current_status']['conversation_duration']}")
    print(f"总干预次数: {dashboard['statistics']['interventions']}")
    print(f"平均紧急度: {dashboard['statistics']['avg_urgency']:.3f}")
    print(f"最高升级等级: {dashboard['statistics']['max_escalation']}")

if __name__ == "__main__":
    asyncio.run(test_context_aware_detection()) 