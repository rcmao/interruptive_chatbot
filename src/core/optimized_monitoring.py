"""
优化监控系统 - 核心冲突检测模块
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class MessageData:
    """消息数据结构"""
    content: str
    author: str
    timestamp: datetime
    channel_id: str

@dataclass
class ConflictSignal:
    """冲突信号"""
    signal_type: str
    value: float
    confidence: float
    timestamp: datetime

class OptimizedConflictMonitor:
    """优化冲突监控器"""
    
    def __init__(self):
        self.conflict_threshold = 0.65
        self.intervention_cooldown = 300
        self.last_intervention = {}
    
    async def process_message(self, message: MessageData) -> Optional[Dict]:
        """处理消息并检测冲突"""
        try:
            # 冲突检测
            conflict_score = await self.detect_conflict(message)
            
            # 检查是否需要干预
            if conflict_score > self.conflict_threshold:
                if self.should_intervene(message.channel_id):
                    return {
                        'intervention_needed': True,
                        'conflict_score': conflict_score,
                        'strategy': self.select_strategy(conflict_score)
                    }
            
            return {
                'intervention_needed': False,
                'conflict_score': conflict_score
            }
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            return None
    
    async def detect_conflict(self, message: MessageData) -> float:
        """检测冲突分数"""
        # 简单的冲突检测逻辑
        conflict_keywords = ["总是", "受够了", "不理解", "苛刻", "挂科", "愤怒", "不满"]
        emotional_keywords = ["担忧", "愧疚", "困难", "压力"]
        
        content = message.content.lower()
        score = 0.0
        
        # 关键词检测
        for keyword in conflict_keywords:
            if keyword in content:
                score += 0.3
        
        for keyword in emotional_keywords:
            if keyword in content:
                score += 0.2
        
        return min(score, 1.0)
    
    def should_intervene(self, channel_id: str) -> bool:
        """检查是否应该干预"""
        now = datetime.now()
        if channel_id in self.last_intervention:
            time_diff = (now - self.last_intervention[channel_id]).total_seconds()
            return time_diff > self.intervention_cooldown
        return True
    
    def select_strategy(self, conflict_score: float) -> str:
        """选择干预策略"""
        if conflict_score > 0.8:
            return "avoiding"
        elif conflict_score > 0.6:
            return "accommodating"
        else:
            return "collaborating"
