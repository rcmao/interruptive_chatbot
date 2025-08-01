"""
可解释性增强的实时冲突干预系统
解决Thomas模型与LLM打分冲突问题
"""

import asyncio
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConflictEvidence(Enum):
    """冲突证据类型"""
    KEYWORD_BASED = "keyword"           # 关键词证据
    LINGUISTIC_PATTERN = "linguistic"   # 语言模式证据  
    EMOTIONAL_INDICATOR = "emotional"   # 情绪指标证据
    BEHAVIORAL_SIGNAL = "behavioral"    # 行为信号证据
    CONTEXTUAL_TREND = "contextual"     # 上下文趋势证据
    LLM_SEMANTIC = "llm_semantic"       # LLM语义理解证据

class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"       # >0.8
    MEDIUM = "medium"   # 0.5-0.8
    LOW = "low"         # 0.3-0.5
    UNCERTAIN = "uncertain"  # <0.3

@dataclass
class ConflictSignal:
    """单个冲突信号"""
    signal_type: ConflictEvidence
    value: float  # 0-1
    confidence: float  # 0-1
    evidence_text: str
    processing_time: float
    explanation: str

@dataclass
class ExplainableDecision:
    """可解释的决策结果"""
    should_intervene: bool
    confidence_level: ConfidenceLevel
    thomas_stage: str
    intervention_reason: str
    evidence_chain: List[ConflictSignal]
    conflicting_signals: List[ConflictSignal]
    processing_breakdown: Dict[str, float]
    fallback_used: bool

class HybridConflictAnalyzer:
    """混合冲突分析器 - 解决模型冲突"""
    
    def __init__(self):
        self.lightweight_threshold = 0.4   # 快速检测阈值
        self.thomas_weight = 0.4          # Thomas模型权重
        self.llm_weight = 0.3             # LLM权重
        self.keyword_weight = 0.3         # 关键词权重
        
        # 实时性优先级
        self.max_llm_wait_time = 400  # ms
        self.early_decision_threshold = 0.7
        
    async def analyze_with_explanation(self, message: str, context: dict) -> ExplainableDecision:
        """带解释的冲突分析"""
        start_time = asyncio.get_event_loop().time()
        signals = []
        
        # 1. 立即启动并行分析
        tasks = [
            self._lightweight_analysis(message),
            self._thomas_stage_analysis(message, context),
            self._llm_analysis_with_timeout(message, context)
        ]
        
        # 2. 等待快速分析完成
        lightweight_signal, thomas_signal = await asyncio.gather(*tasks[:2])
        signals.extend([lightweight_signal, thomas_signal])
        
        # 3. 早期决策检查
        early_decision = self._check_early_decision(signals)
        if early_decision:
            return self._build_decision(signals, early_decision=True, 
                                      processing_time=asyncio.get_event_loop().time() - start_time)
        
        # 4. 等待LLM分析（有超时）
        try:
            llm_signal = await asyncio.wait_for(tasks[2], timeout=0.4)
            signals.append(llm_signal)
        except asyncio.TimeoutError:
            logger.warning("LLM分析超时，使用快速分析结果")
            llm_signal = ConflictSignal(
                signal_type=ConflictEvidence.LLM_SEMANTIC,
                value=0.0,
                confidence=0.0,
                evidence_text="超时",
                processing_time=400,
                explanation="LLM分析超时，使用本地分析"
            )
            signals.append(llm_signal)
        
        # 5. 综合决策
        return self._build_decision(signals, early_decision=False,
                                  processing_time=asyncio.get_event_loop().time() - start_time)
    
    async def _lightweight_analysis(self, message: str) -> ConflictSignal:
        """轻量级分析"""
        start_time = asyncio.get_event_loop().time()
        
        conflict_indicators = {
            "emotion_words": ["愤怒", "生气", "不满", "angry", "frustrated"],
            "disagreement": ["不同意", "反对", "错误", "wrong", "disagree"],
            "personal_attack": ["你总是", "你从不", "you always", "you never"],
            "intensity": ["!", "完全", "绝对", "absolutely", "completely"]
        }
        
        score = 0.0
        evidence = []
        
        for category, keywords in conflict_indicators.items():
            count = sum(1 for word in keywords if word.lower() in message.lower())
            if count > 0:
                category_score = min(count * 0.2, 0.4)
                score += category_score
                evidence.append(f"{category}: {count}个匹配")
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return ConflictSignal(
            signal_type=ConflictEvidence.KEYWORD_BASED,
            value=min(score, 1.0),
            confidence=0.8 if score > 0.3 else 0.5,
            evidence_text="; ".join(evidence),
            processing_time=processing_time,
            explanation=f"关键词匹配分析: {score:.2f}分"
        )
    
    async def _thomas_stage_analysis(self, message: str, context: dict) -> ConflictSignal:
        """Thomas阶段分析"""
        start_time = asyncio.get_event_loop().time()
        
        stage_indicators = {
            "frustration": ["挫折", "阻碍", "frustrated", "blocked"],
            "conceptualization": ["我认为", "问题是", "I think", "the issue"],
            "behavior": ["我要", "我会", "I will", "going to"],
            "interaction": ["你说", "you said", "回应", "respond"],
            "outcomes": ["结果", "后果", "result", "consequence"]
        }
        
        stage_scores = {}
        for stage, keywords in stage_indicators.items():
            score = sum(1 for word in keywords if word.lower() in message.lower())
            stage_scores[stage] = score
        
        # 找到最高分阶段
        max_stage = max(stage_scores, key=stage_scores.get) if any(stage_scores.values()) else "unknown"
        max_score = stage_scores.get(max_stage, 0)
        
        # 判断是否为最佳干预时机
        is_optimal_timing = (max_stage == "conceptualization" and max_score > 0)
        
        conflict_value = 0.6 if is_optimal_timing else min(max_score * 0.2, 0.5)
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return ConflictSignal(
            signal_type=ConflictEvidence.BEHAVIORAL_SIGNAL,
            value=conflict_value,
            confidence=0.9 if is_optimal_timing else 0.6,
            evidence_text=f"阶段: {max_stage}, 分数: {max_score}",
            processing_time=processing_time,
            explanation=f"Thomas模型识别为{max_stage}阶段，最佳时机: {is_optimal_timing}"
        )
    
    async def _llm_analysis_with_timeout(self, message: str, context: dict) -> ConflictSignal:
        """带超时的LLM分析"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 模拟LLM API调用
            await asyncio.sleep(0.3)  # 模拟300ms延迟
            
            # 简化的LLM分析逻辑
            score = 0.5 if any(word in message.lower() for word in ["冲突", "争吵", "分歧"]) else 0.3
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return ConflictSignal(
                signal_type=ConflictEvidence.LLM_SEMANTIC,
                value=score,
                confidence=0.8,
                evidence_text="语义分析完成",
                processing_time=processing_time,
                explanation=f"LLM语义理解分析: {score:.2f}分"
            )
            
        except Exception as e:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return ConflictSignal(
                signal_type=ConflictEvidence.LLM_SEMANTIC,
                value=0.0,
                confidence=0.0,
                evidence_text=f"分析失败: {str(e)}",
                processing_time=processing_time,
                explanation="LLM分析失败，使用本地分析"
            )
    
    def _check_early_decision(self, signals: List[ConflictSignal]) -> Optional[bool]:
        """检查是否可以早期决策"""
        # 如果Thomas模型高置信度识别最佳时机
        thomas_signal = next((s for s in signals if s.signal_type == ConflictEvidence.BEHAVIORAL_SIGNAL), None)
        if thomas_signal and thomas_signal.confidence > 0.8 and thomas_signal.value > 0.5:
            return True
        
        # 如果关键词检测高分
        keyword_signal = next((s for s in signals if s.signal_type == ConflictEvidence.KEYWORD_BASED), None)
        if keyword_signal and keyword_signal.value > self.early_decision_threshold:
            return True
        
        return None
    
    def _build_decision(self, signals: List[ConflictSignal], early_decision: bool, processing_time: float) -> ExplainableDecision:
        """构建可解释的决策"""
        
        # 计算加权分数
        total_score = 0.0
        total_weight = 0.0
        evidence_chain = []
        conflicting_signals = []
        
        weights = {
            ConflictEvidence.KEYWORD_BASED: self.keyword_weight,
            ConflictEvidence.BEHAVIORAL_SIGNAL: self.thomas_weight,
            ConflictEvidence.LLM_SEMANTIC: self.llm_weight
        }
        
        for signal in signals:
            weight = weights.get(signal.signal_type, 0.1)
            if signal.confidence > 0.3:  # 只考虑高置信度信号
                total_score += signal.value * weight * signal.confidence
                total_weight += weight * signal.confidence
                evidence_chain.append(signal)
            else:
                conflicting_signals.append(signal)
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # 决策逻辑
        should_intervene = final_score > 0.35
        
        # 置信度等级
        if final_score > 0.8:
            confidence_level = ConfidenceLevel.HIGH
        elif final_score > 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        elif final_score > 0.3:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.UNCERTAIN
        
        # Thomas阶段判断
        thomas_signal = next((s for s in signals if s.signal_type == ConflictEvidence.BEHAVIORAL_SIGNAL), None)
        thomas_stage = thomas_signal.evidence_text.split(",")[0] if thomas_signal else "未知"
        
        # 干预原因
        intervention_reason = self._generate_intervention_reason(final_score, evidence_chain, early_decision)
        
        # 处理时间分解
        processing_breakdown = {
            signal.signal_type.value: signal.processing_time 
            for signal in signals
        }
        
        return ExplainableDecision(
            should_intervene=should_intervene,
            confidence_level=confidence_level,
            thomas_stage=thomas_stage,
            intervention_reason=intervention_reason,
            evidence_chain=evidence_chain,
            conflicting_signals=conflicting_signals,
            processing_breakdown=processing_breakdown,
            fallback_used=early_decision
        )
    
    def _generate_intervention_reason(self, score: float, evidence: List[ConflictSignal], early_decision: bool) -> str:
        """生成干预原因说明"""
        if score > 0.8:
            return f"高冲突风险 (分数: {score:.2f}) - 检测到强烈冲突信号"
        elif score > 0.5:
            return f"中等冲突风险 (分数: {score:.2f}) - 建议预防性干预"
        elif score > 0.35:
            return f"轻微冲突倾向 (分数: {score:.2f}) - 温和提醒"
        else:
            return f"无需干预 (分数: {score:.2f}) - 对话正常"

class ExplainableInterventionBot:
    """可解释性冲突干预机器人"""
    
    def __init__(self):
        self.analyzer = HybridConflictAnalyzer()
        
    async def process_message_with_explanation(self, message: str, author: str, channel_id: str) -> Optional[str]:
        """处理消息并生成解释"""
        
        # 分析冲突
        decision = await self.analyzer.analyze_with_explanation(
            message, 
            {"channel_id": channel_id, "author": author}
        )
        
        # 记录详细日志
        logger.info(f"🔍 冲突分析结果:")
        logger.info(f"   决策: {'干预' if decision.should_intervene else '不干预'}")
        logger.info(f"   置信度: {decision.confidence_level.value}")
        logger.info(f"   Thomas阶段: {decision.thomas_stage}")
        logger.info(f"   处理时间: {sum(decision.processing_breakdown.values()):.1f}ms")
        
        for signal in decision.evidence_chain:
            logger.info(f"   ✅ {signal.explanation}")
        
        for signal in decision.conflicting_signals:
            logger.info(f"   ⚠️ {signal.explanation}")
        
        if decision.should_intervene:
            # 生成干预消息
            intervention = self._generate_transparent_intervention(decision)
            return intervention
        
        return None
    
    def _generate_transparent_intervention(self, decision: ExplainableDecision) -> str:
        """生成透明的干预消息"""
        
        # 基础干预消息
        base_messages = {
            ConfidenceLevel.HIGH: "我注意到对话中出现了比较强烈的分歧。",
            ConfidenceLevel.MEDIUM: "我感觉到一些紧张气氛。",
            ConfidenceLevel.LOW: "让我们保持冷静继续讨论。"
        }
        
        base_msg = base_messages.get(decision.confidence_level, "我来帮助大家更好地沟通。")
        
        # 添加可解释性信息（调试模式）
        debug_info = f"\n\n💡 干预依据: {decision.intervention_reason}"
        debug_info += f"\n🎯 分析阶段: {decision.thomas_stage}"
        debug_info += f"\n⚡ 响应时间: {sum(decision.processing_breakdown.values()):.0f}ms"
        
        if decision.fallback_used:
            debug_info += "\n🚀 使用快速决策模式"
        
        return base_msg + debug_info

# 使用示例
async def main():
    bot = ExplainableInterventionBot()
    
    # 测试消息
    test_messages = [
        "我觉得你的想法完全错误！",
        "我认为这里的问题是沟通不够",
        "你总是不听我的意见",
        "今天天气不错呢"
    ]
    
    for msg in test_messages:
        print(f"\n📨 测试消息: {msg}")
        result = await bot.process_message_with_explanation(msg, "测试用户", "test_channel")
        if result:
            print(f"🤖 干预: {result}")
        else:
            print("✅ 无需干预")

if __name__ == "__main__":
    asyncio.run(main()) 