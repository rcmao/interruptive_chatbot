"""
统一的检测结果数据类
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from .unified_mapping import UnifiedTriggerType

@dataclass
class UnifiedDetectionResult:
    """统一的检测结果"""
    should_intervene: bool
    trigger_type: UnifiedTriggerType
    urgency_level: int  # 1-5
    confidence: float   # 0-1
    reasoning: str
    evidence: List[str]
    context: Dict = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'should_intervene': self.should_intervene,
            'trigger_type': self.trigger_type.value,
            'urgency_level': self.urgency_level,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'evidence': self.evidence,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UnifiedDetectionResult':
        """从字典创建实例"""
        return cls(
            should_intervene=data['should_intervene'],
            trigger_type=UnifiedTriggerType(data['trigger_type']),
            urgency_level=data['urgency_level'],
            confidence=data['confidence'],
            reasoning=data['reasoning'],
            evidence=data['evidence'],
            context=data.get('context', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        ) 