"""
优化版上下文感知冲突检测器
解决上下文过度影响的问题
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime

class ContextOptimizedDetector:
    """优化版上下文感知检测器"""
    
    def __init__(self):
        # 保持原有的关键词分类
        self.conflict_keywords = {
            "severe": [
                "荒谬", "愚蠢", "错误", "不对", "不行", "受够了", "无理取闹", 
                "你错了", "你根本不懂", "你才是什么都不懂", "我受够了"
            ],
            "moderate": [
                "总是", "从不", "挑毛病", "不负责任", "借口", "固执", 
                "你总是", "你从不", "你凭什么", "我对你的表现很不满"
            ],
            "mild": [
                "不同意", "反对", "问题", "考虑不周全", "不同意见", 
                "有点问题", "不太同意", "质疑"
            ]
        }
        
        # 优化阈值设置
        self.base_threshold = 0.35
        self.context_threshold = 0.25
        self.severe_threshold = 0.6
        
        # 上下文权重衰减
        self.context_decay_factor = 0.7  # 上下文影响随时间衰减
    
    def detect_conflict(self, content: str, context: List[str] = None) -> Tuple[bool, float, str]:
        """优化的冲突检测，减少上下文过度影响"""
        content_lower = content.lower()
        score = 0.0
        reasons = []
        
        # 1. 基础冲突检测（主要权重）
        base_score = self._calculate_base_score(content_lower, reasons)
        score += base_score
        
        # 2. 优化的上下文分析（降低权重）
        if context and len(context) >= 2:
            context_score = self._calculate_optimized_context_score(content_lower, context, reasons)
            score += context_score * self.context_decay_factor  # 应用衰减因子
        
        # 3. 动态阈值调整
        dynamic_threshold = self._calculate_dynamic_threshold(base_score, context)
        
        # 限制总分在0-1之间
        score = min(1.0, score)
        
        # 判断是否需要干预
        should_intervene = score > dynamic_threshold
        
        return should_intervene, score, "; ".join(reasons)
    
    def _calculate_base_score(self, content_lower: str, reasons: List[str]) -> float:
        """计算基础冲突分数"""
        score = 0.0
        
        # 严重冲突关键词 (权重: 50%)
        for keyword in self.conflict_keywords["severe"]:
            if keyword in content_lower:
                score += 0.5
                reasons.append(f"严重冲突: {keyword}")
        
        # 中等冲突关键词 (权重: 35%)
        for keyword in self.conflict_keywords["moderate"]:
            if keyword in content_lower:
                score += 0.35
                reasons.append(f"中等冲突: {keyword}")
        
        # 轻微冲突关键词 (权重: 15%)
        for keyword in self.conflict_keywords["mild"]:
            if keyword in content_lower:
                score += 0.15
                reasons.append(f"轻微冲突: {keyword}")
        
        # 情绪关键词 (权重: 30%)
        emotion_keywords = {
            "anger": ["愤怒", "生气", "恼火", "愤慨", "angry", "mad", "furious"],
            "frustration": ["挫折", "沮丧", "失望", "frustrated", "disappointed", "不满"],
            "defensive": ["凭什么", "你才", "我受够了", "你总是", "你从不", "质疑我的想法"]
        }
        
        for emotion_type, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    if emotion_type == "anger":
                        score += 0.4
                    elif emotion_type == "frustration":
                        score += 0.3
                    elif emotion_type == "defensive":
                        score += 0.25
                    reasons.append(f"情绪: {keyword}")
        
        # 冲突模式 (权重: 20%)
        conflict_patterns = [
            r"你总是.*", r"你从不.*", r"你凭什么.*",
            r".*太.*了", r".*完全.*错.*"
        ]
        
        for pattern in conflict_patterns:
            if re.search(pattern, content_lower):
                score += 0.3
                reasons.append(f"冲突模式: {pattern}")
        
        # 强度标记 (权重: 10%)
        intensity_markers = ["！", "!!", "？？", "??"]
        intensity_count = sum(1 for marker in intensity_markers if marker in content_lower)
        if intensity_count > 0:
            score += intensity_count * 0.1
            reasons.append(f"强度标记: {intensity_count}个")
        
        return score
    
    def _calculate_optimized_context_score(self, content_lower: str, context: List[str], reasons: List[str]) -> float:
        """优化的上下文分数计算"""
        context_score = 0.0
        
        # 只检查最近2条消息中的严重冲突
        recent_messages = context[-2:]
        severe_conflict_count = 0
        
        for ctx_msg in recent_messages:
            ctx_lower = ctx_msg.lower()
            # 只计算严重冲突关键词
            if any(kw in ctx_lower for kw in self.conflict_keywords["severe"]):
                severe_conflict_count += 1
        
        # 只有当当前消息本身有轻微冲突且上下文有严重冲突时才增加分数
        current_has_mild = any(kw in content_lower for kw in self.conflict_keywords["mild"])
        
        if severe_conflict_count >= 1 and current_has_mild:
            context_score = 0.15
            reasons.append(f"上下文增强: {severe_conflict_count}条严重冲突")
        
        return context_score
    
    def _calculate_dynamic_threshold(self, base_score: float, context: List[str] = None) -> float:
        """计算动态阈值"""
        threshold = self.base_threshold
        
        # 如果有严重冲突，降低阈值
        if base_score >= 0.5:
            threshold = self.severe_threshold
        
        # 上下文影响（更保守）
        if context and len(context) >= 2:
            # 只检查是否有严重冲突的上下文
            has_severe_context = any(
                any(kw in ctx.lower() for kw in self.conflict_keywords["severe"])
                for ctx in context[-2:]
            )
            if has_severe_context:
                threshold = min(threshold, self.context_threshold)
        
        return threshold 