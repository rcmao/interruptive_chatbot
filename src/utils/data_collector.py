"""
针对实验需求的数据收集系统
"""

class ExperimentDataCollector:
    """实验数据收集器"""
    
    def __init__(self):
        self.conversation_logs = []
        self.intervention_logs = []
        self.emotion_timeline = []
    
    def log_message(self, message: str, author: str, role: str, timestamp: datetime):
        """记录消息"""
        self.conversation_logs.append({
            "timestamp": timestamp,
            "author": author,
            "role": role,
            "message": message,
            "message_length": len(message),
            "emotion_indicators": self._extract_emotion_indicators(message)
        })
    
    def log_intervention(self, intervention: str, trigger_reason: str, confidence: float, 
                        processing_time: float, context: dict):
        """记录干预"""
        self.intervention_logs.append({
            "timestamp": datetime.now(),
            "intervention_message": intervention,
            "trigger_reason": trigger_reason,
            "confidence": confidence,
            "processing_time": processing_time,
            "context": context,
            "conversation_turn": len(self.conversation_logs)
        })
    
    def track_emotion_progression(self, emotion_score: float, thomas_stage: str):
        """追踪情绪变化"""
        self.emotion_timeline.append({
            "timestamp": datetime.now(),
            "emotion_score": emotion_score,
            "thomas_stage": thomas_stage,
            "turn_number": len(self.conversation_logs)
        })
    
    def generate_experiment_report(self) -> dict:
        """生成实验报告"""
        return {
            "conversation_summary": {
                "total_messages": len(self.conversation_logs),
                "total_interventions": len(self.intervention_logs),
                "intervention_rate": len(self.intervention_logs) / max(len(self.conversation_logs), 1),
                "average_processing_time": sum(log["processing_time"] for log in self.intervention_logs) / max(len(self.intervention_logs), 1)
            },
            "emotion_analysis": {
                "emotion_trajectory": [e["emotion_score"] for e in self.emotion_timeline],
                "thomas_stage_progression": [e["thomas_stage"] for e in self.emotion_timeline],
                "peak_emotion_score": max([e["emotion_score"] for e in self.emotion_timeline], default=0)
            },
            "intervention_effectiveness": {
                "interventions_per_stage": self._count_interventions_per_stage(),
                "response_time_distribution": [log["processing_time"] for log in self.intervention_logs]
            }
        } 