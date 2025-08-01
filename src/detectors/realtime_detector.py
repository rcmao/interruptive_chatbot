"""
针对实验实时性要求的优化检测系统
目标: <300ms 响应时间
"""

class UltraFastConflictDetector:
    """超快速冲突检测器"""
    
    def __init__(self):
        # 预编译正则表达式
        import re
        self.compiled_patterns = {
            "high_urgency": re.compile(r"(受够了|愤怒|生气|不能容忍|fed up|angry|furious)", re.IGNORECASE),
            "medium_urgency": re.compile(r"(不满|担心|失望|upset|worried|disappointed)", re.IGNORECASE),
            "escalation": re.compile(r"(你总是|你从来|为什么|you always|you never|why)", re.IGNORECASE)
        }
        
        # 场景特定的快速检测规则
        self.quick_rules = [
            {"pattern": "连续.*缺席", "score": 0.6, "reason": "提到连续缺席"},
            {"pattern": "没有.*提交", "score": 0.5, "reason": "提到未提交任务"},
            {"pattern": "你.*做错", "score": 0.4, "reason": "指责对方"},
            {"pattern": "我.*愧疚", "score": 0.3, "reason": "表达愧疚"},
        ]
    
    async def ultra_fast_detect(self, message: str, role: str) -> dict:
        """超快速检测 (<50ms)"""
        start_time = time.time()
        
        total_score = 0.0
        reasons = []
        
        # 1. 预编译正则匹配 (~10ms)
        for urgency, pattern in self.compiled_patterns.items():
            if pattern.search(message):
                score_map = {"high_urgency": 0.8, "medium_urgency": 0.5, "escalation": 0.7}
                total_score += score_map[urgency]
                reasons.append(f"检测到{urgency}")
        
        # 2. 快速规则匹配 (~20ms)
        import re
        for rule in self.quick_rules:
            if re.search(rule["pattern"], message, re.IGNORECASE):
                total_score += rule["score"]
                reasons.append(rule["reason"])
        
        # 3. 角色权重调整 (~5ms)
        if role == "leader" and total_score > 0.4:
            total_score *= 1.2  # 组长情绪更容易触发干预
        elif role == "member" and total_score > 0.3:
            total_score *= 1.1  # 组员防御也需要关注
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "score": min(total_score, 1.0),
            "should_intervene": total_score > 0.35,
            "reasons": reasons,
            "processing_time": processing_time,
            "confidence": 0.8 if reasons else 0.3
        } 