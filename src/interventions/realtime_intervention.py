"""
实时干预系统 - 集成TKI策略和上下文感知
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import deque
import logging

from optimized_monitoring_fixed import OptimizedConflictMonitorFixed
from intervention_generator import TKIInterventionGenerator, TKIStrategy, ConflictPhase

logger = logging.getLogger(__name__)

class RealTimeInterventionSystem:
    """实时干预系统"""
    
    def __init__(self, api_key: str, api_base: str):
        self.conflict_monitor = OptimizedConflictMonitorFixed(api_key, api_base)
        self.intervention_generator = TKIInterventionGenerator()
        self.recent_interventions = deque(maxlen=10)
        self.context_tracker = ContextTracker()
        
        # 干预控制参数
        self.min_intervention_interval = 30  # 最小干预间隔（秒）
        self.max_interventions_per_hour = 6  # 每小时最大干预次数
        
    async def initialize(self):
        """初始化系统"""
        await self.conflict_monitor.initialize()
        logger.info("🚀 实时干预系统已初始化")
    
    async def process_message_with_intervention(self, message_data, channel) -> Optional[str]:
        """处理消息并在需要时进行干预"""
        
        # 1. 冲突检测
        should_intervene, score, reason, signals = await self.conflict_monitor.process_message(message_data)
        
        # 2. 更新上下文
        context = self.context_tracker.update_context(message_data, signals)
        
        # 3. 干预决策
        if should_intervene and self._can_intervene():
            
            # 选择TKI策略
            strategy = self.intervention_generator.select_strategy(signals, context)
            
            # 评估冲突阶段
            phase = self.intervention_generator._assess_conflict_phase(signals, context)
            
            # 生成干预消息
            intervention_message = self.intervention_generator.generate_intervention(
                strategy, phase, context
            )
            
            # 记录干预
            self._record_intervention(strategy, phase, score, intervention_message)
            
            # 发送干预消息
            await self._send_intervention(channel, intervention_message)
            
            logger.info(f"🤖 干预执行: 策略={strategy.value}, 阶段={phase.value}, 分数={score:.2f}")
            
            return intervention_message
        
        return None
    
    def _can_intervene(self) -> bool:
        """检查是否可以进行干预"""
        now = datetime.now()
        
        # 检查最小间隔
        if self.recent_interventions:
            last_intervention = self.recent_interventions[-1]["timestamp"]
            if (now - last_intervention).seconds < self.min_intervention_interval:
                return False
        
        # 检查每小时频率
        recent_hour_interventions = [
            i for i in self.recent_interventions 
            if (now - i["timestamp"]).seconds < 3600
        ]
        
        if len(recent_hour_interventions) >= self.max_interventions_per_hour:
            return False
        
        return True
    
    def _record_intervention(self, strategy: TKIStrategy, phase: ConflictPhase, 
                           score: float, message: str):
        """记录干预信息"""
        self.recent_interventions.append({
            "timestamp": datetime.now(),
            "strategy": strategy,
            "phase": phase,
            "score": score,
            "message": message
        })
    
    async def _send_intervention(self, channel, message: str):
        """发送干预消息到Discord频道"""
        try:
            await channel.send(message)
        except Exception as e:
            logger.error(f"❌ 发送干预消息失败: {e}")
    
    def get_intervention_stats(self) -> Dict:
        """获取干预统计"""
        if not self.recent_interventions:
            return {"total": 0, "strategies": {}, "phases": {}}
        
        strategies = {}
        phases = {}
        
        for intervention in self.recent_interventions:
            strategy = intervention["strategy"].value
            phase = intervention["phase"].value
            
            strategies[strategy] = strategies.get(strategy, 0) + 1
            phases[phase] = phases.get(phase, 0) + 1
        
        return {
            "total": len(self.recent_interventions),
            "strategies": strategies,
            "phases": phases,
            "avg_score": sum(i["score"] for i in self.recent_interventions) / len(self.recent_interventions)
        }

class ContextTracker:
    """上下文跟踪器"""
    
    def __init__(self):
        self.participants = set()
        self.message_history = deque(maxlen=20)
        self.topic_keywords = []
        
    def update_context(self, message_data, signals: Dict) -> Dict:
        """更新上下文信息"""
        
        # 跟踪参与者
        self.participants.add(message_data.author_name)
        
        # 更新消息历史
        self.message_history.append({
            "author": message_data.author_name,
            "content": message_data.content,
            "timestamp": message_data.timestamp
        })
        
        # 提取关键词
        self._extract_topic_keywords(message_data.content)
        
        return {
            "participants": list(self.participants),
            "message_count": len(self.message_history),
            "topic_keywords": self.topic_keywords[-5:],  # 最近5个关键词
            "goal": self._infer_goal(),
            "core_issue": self._identify_core_issue()
        }
    
    def _extract_topic_keywords(self, content: str):
        """提取话题关键词（简化版本）"""
        # 简单的关键词提取
        important_words = ["任务", "项目", "汇报", "PPT", "小组", "讨论", "计划"]
        
        for word in important_words:
            if word in content and word not in self.topic_keywords:
                self.topic_keywords.append(word)
    
    def _infer_goal(self) -> str:
        """推断对话目标"""
        if "汇报" in self.topic_keywords or "PPT" in self.topic_keywords:
            return "完成课程汇报"
        elif "项目" in self.topic_keywords:
            return "完成项目任务"
        else:
            return "解决当前问题"
    
    def _identify_core_issue(self) -> str:
        """识别核心问题"""
        recent_messages = list(self.message_history)[-5:]
        
        if any("缺席" in msg["content"] or "没来" in msg["content"] for msg in recent_messages):
            return "参与度问题"
        elif any("提交" in msg["content"] or "完成" in msg["content"] for msg in recent_messages):
            return "任务完成问题"
        else:
            return "沟通协调问题" 