"""
修复版本的监控系统 - 更敏感的冲突检测
"""

import asyncio
import aiohttp
import openai
import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque, defaultdict
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SignalResult:
    """信号检测结果"""
    signal_type: str
    value: float
    confidence: float
    processing_time: float
    timestamp: datetime

@dataclass
class RealTimeMetrics:
    """实时性能指标"""
    total_processing_time: float = 0.0
    llm_processing_time: float = 0.0
    local_processing_time: float = 0.0
    signal_count: int = 0
    intervention_count: int = 0
    avg_response_time: float = 0.0

class LightweightConflictDetectorFixed:
    """修复版本的轻量级冲突检测器 - 更敏感"""
    
    def __init__(self):
        self.emotion_keywords = {
            "anger": ["愤怒", "生气", "恼火", "愤慨", "angry", "mad", "furious"],
            "frustration": ["挫折", "沮丧", "失望", "frustrated", "disappointed"],
            "disagreement": ["不同意", "反对", "错误", "不合理", "disagree", "wrong", "incorrect", "unreasonable"],
            "negative": ["荒谬", "愚蠢", "无理", "ridiculous", "stupid", "unreasonable", "完全", "绝对"],
            "personal": ["你从不", "你总是", "你错了", "you never", "you always", "you're wrong"],
            "strong": ["完全", "绝对", "太", "非常", "extremely", "completely", "absolutely"]
        }
        
    def quick_score(self, content: str, context: List[str] = None) -> float:
        """快速冲突分数计算 - 更敏感的版本"""
        if not content:
            return 0.0
        
        score = 0.0
        content_lower = content.lower()
        
        # 关键词检测 - 增加权重
        for category, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # 不同类型关键词给不同权重
                    if category == "personal":
                        score += 0.3  # 人身攻击权重最高
                    elif category == "negative":
                        score += 0.25  # 负面词汇权重很高
                    elif category == "strong":
                        score += 0.2   # 强调词汇
                    elif category == "disagreement":
                        score += 0.15  # 分歧词汇
                    else:
                        score += 0.1
        
        # 语气强度检测 - 增加权重
        if "!" in content:
            score += 0.15  # 感叹号权重增加
        if "？" in content:
            score += 0.08
        if content.isupper():  # 全大写
            score += 0.2
        
        # 特殊模式检测
        if "不行" in content or "不可以" in content:
            score += 0.2
        if "从不" in content or "总是" in content:
            score += 0.25
        if "never" in content_lower or "always" in content_lower:
            score += 0.25
        
        # 上下文分析 - 增加权重
        if context:
            context_str = " ".join(context).lower()
            if any(word in context_str for word in ["冲突", "争论", "分歧", "conflict", "argue"]):
                score += 0.15
        
        return min(score, 1.0)

class AsyncLLMProcessorFixed:
    """修复版本的异步LLM处理器"""
    
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
        self.client = None
        
    async def initialize(self):
        """初始化OpenAI客户端"""
        try:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            logger.info("✅ OpenAI客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ OpenAI客户端初始化失败: {e}")
            self.client = None
    
    async def predictive_score(self, messages: List[str], priority: str = "normal") -> float:
        """预测性冲突评分"""
        if not self.client:
            logger.warning("⚠️  API客户端未初始化，使用本地评分")
            return self._local_fallback_score(messages)
        
        try:
            # 使用同步客户端的异步包装
            score = await asyncio.get_event_loop().run_in_executor(
                None, self._compute_llm_score_sync, messages
            )
            return score
        except Exception as e:
            logger.warning(f"⚠️  LLM评分失败，使用本地评分: {e}")
            return self._local_fallback_score(messages)
    
    def _compute_llm_score_sync(self, messages: List[str]) -> float:
        """同步计算LLM冲突分数"""
        prompt = f"""
快速分析对话冲突程度(0-1分，0.3以上表示需要关注):

最近对话:
{chr(10).join(messages[-3:])}

评分标准:
- 0-0.2: 正常讨论
- 0.3-0.5: 轻微分歧，需要关注
- 0.6-0.8: 明显冲突，建议干预
- 0.9-1.0: 激烈冲突，立即干预

只返回数字分数，例如: 0.7
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10,
                timeout=3  # 减少超时时间
            )
            
            score_text = response.choices[0].message.content.strip()
            
            import re
            match = re.search(r'0\.\d+|1\.0|0|1', score_text)
            return float(match.group()) if match else 0.5
            
        except Exception as e:
            logger.warning(f"LLM API调用失败: {e}")
            return 0.5
    
    def _local_fallback_score(self, messages: List[str]) -> float:
        """本地回退评分算法 - 更敏感"""
        if not messages:
            return 0.0
        
        # 扩展的冲突关键词
        conflict_keywords = [
            "错误", "荒谬", "愚蠢", "不行", "反对", "不同意", "不合理",
            "wrong", "ridiculous", "stupid", "disagree", "never", "always",
            "完全", "绝对", "太", "从不", "总是"
        ]
        
        score = 0.0
        recent_messages = messages[-3:]  # 最近3条消息
        
        for message in recent_messages:
            content = message.lower()
            keyword_count = sum(1 for keyword in conflict_keywords if keyword in content)
            score += keyword_count * 0.15  # 增加权重
        
        # 消息长度和语气
        if recent_messages:
            last_message = recent_messages[-1]
            if "!" in last_message:
                score += 0.15
            if "？" in last_message:
                score += 0.08
            if len(last_message) < 10:  # 短消息可能更情绪化
                score += 0.1
        
        return min(score, 1.0)

class IntelligentTriggerLogicFixed:
    """修复版本的智能触发逻辑 - 更敏感的阈值"""
    
    def __init__(self):
        # 大幅降低阈值，提高敏感性
        self.base_threshold = 0.2  # 从0.35进一步降低到0.2
        self.recent_interventions = deque(maxlen=10)
        
    def should_intervene(self, signal_results: Dict[str, SignalResult]) -> Tuple[bool, float, str]:
        """判断是否需要干预 - 更敏感的逻辑"""
        
        # 安全地获取各种信号分数
        llm_score = signal_results.get("llm").value if signal_results.get("llm") else 0.0
        lightweight_score = signal_results.get("lightweight").value if signal_results.get("lightweight") else 0.0
        emotion_score = signal_results.get("emotion").value if signal_results.get("emotion") else 0.0
        turn_taking_score = signal_results.get("turn_taking").value if signal_results.get("turn_taking") else 0.0
        
        # 多信号融合算法 - 调整权重
        final_score = (
            lightweight_score * 0.5 +     # 轻量级检测权重提高到50%
            emotion_score * 0.25 +         # 情绪检测权重25%
            llm_score * 0.15 +             # LLM评分权重15%
            turn_taking_score * 0.1        # 发言权检测权重10%
        )
        
        # 动态阈值调整
        adjusted_threshold = self.base_threshold
        
        # 如果最近有干预，略微提高阈值避免过度干预
        recent_interventions = len([
            t for t in self.recent_interventions 
            if (datetime.now() - t).seconds < 180  # 减少到3分钟内
        ])
        
        if recent_interventions > 0:
            adjusted_threshold += 0.05 * recent_interventions  # 减少调整幅度
        
        # 特殊情况触发器 - 降低阈值
        high_emotion_trigger = (
            emotion_score > 0.3 and 
            (lightweight_score > 0.15 or turn_taking_score > 0.15)
        )
        
        # 强烈冲突关键词触发 - 降低阈值
        strong_conflict_trigger = lightweight_score > 0.25
        
        # LLM高分触发
        llm_high_trigger = llm_score > 0.4
        
        # 决策逻辑
        should_intervene = (
            final_score >= adjusted_threshold or 
            high_emotion_trigger or
            strong_conflict_trigger or
            llm_high_trigger
        )
        
        # 记录干预
        if should_intervene:
            self.recent_interventions.append(datetime.now())
        
        # 生成原因
        reason = self._generate_reason(final_score, adjusted_threshold, signal_results, 
                                     high_emotion_trigger, strong_conflict_trigger, llm_high_trigger)
        
        return should_intervene, final_score, reason
    
    def _generate_reason(self, score: float, threshold: float, signals: Dict, 
                        high_emotion: bool, strong_conflict: bool, llm_high: bool) -> str:
        """生成干预原因"""
        if llm_high:
            llm_score = signals.get("llm").value if signals.get("llm") else 0.0
            return f"LLM检测到高冲突(分数:{llm_score:.2f})"
        
        if strong_conflict:
            lightweight_score = signals.get("lightweight").value if signals.get("lightweight") else 0.0
            return f"检测到强烈冲突关键词(分数:{lightweight_score:.2f})"
        
        if high_emotion:
            emotion_score = signals.get("emotion").value if signals.get("emotion") else 0.0
            return f"检测到高情绪化表达(分数:{emotion_score:.2f})"
        
        if score >= threshold:
            return f"综合冲突分数{score:.2f}超过阈值{threshold:.2f}"
        
        return "多信号综合触发"

class ParallelSignalProcessorFixed:
    """修复版本的并行信号处理器"""
    
    def __init__(self, api_key: str, api_base: str):
        self.lightweight_detector = LightweightConflictDetectorFixed()
        self.llm_processor = AsyncLLMProcessorFixed(api_key, api_base)
        self.message_history = deque(maxlen=10)
        self.metrics = RealTimeMetrics()
        
    async def initialize(self):
        """初始化处理器"""
        await self.llm_processor.initialize()
        
    async def process_signals_parallel(self, message_data) -> Dict[str, SignalResult]:
        """并行处理所有信号"""
        start_time = time.time()
        
        # 更新历史记录
        self.message_history.append(message_data)
        context = [f"{msg.author_name}: {msg.content}" for msg in list(self.message_history)]
        
        # 创建并行任务
        tasks = [
            self._process_lightweight_score(message_data.content, context),
            self._process_emotion_detection(message_data.content),
            self._process_turn_taking(list(self.message_history)),
        ]
        
        # 并行执行本地信号检测
        local_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 异步启动LLM处理
        llm_task = asyncio.create_task(
            self._process_llm_score(context, message_data)
        )
        
        # 组装结果
        results = {}
        signal_names = ["lightweight", "emotion", "turn_taking"]
        
        for i, result in enumerate(local_results):
            if not isinstance(result, Exception):
                results[signal_names[i]] = result
        
        # 等待LLM结果
        try:
            llm_result = await asyncio.wait_for(llm_task, timeout=1.5)  # 进一步减少超时时间
            results["llm"] = llm_result
        except asyncio.TimeoutError:
            logger.warning("LLM处理超时，使用本地评分")
            # 使用本地评分作为LLM回退
            local_score = self.lightweight_detector.quick_score(message_data.content, context)
            results["llm"] = SignalResult("llm", local_score * 0.8, 0.5, 0.0, datetime.now())
        except Exception as e:
            logger.warning(f"LLM处理失败: {e}")
            local_score = self.lightweight_detector.quick_score(message_data.content, context)
            results["llm"] = SignalResult("llm", local_score * 0.8, 0.5, 0.0, datetime.now())
        
        # 更新指标
        self.metrics.signal_count += 1
        processing_time = time.time() - start_time
        self.metrics.total_processing_time = processing_time
        
        return results
    
    async def _process_lightweight_score(self, content: str, context: List[str]) -> SignalResult:
        """处理轻量级评分"""
        start_time = time.time()
        score = self.lightweight_detector.quick_score(content, context)
        processing_time = time.time() - start_time
        
        return SignalResult("lightweight", score, 0.9, processing_time, datetime.now())
    
    async def _process_emotion_detection(self, content: str) -> SignalResult:
        """处理情绪检测 - 更敏感"""
        start_time = time.time()
        
        # 扩展的情绪关键词检测
        emotion_keywords = [
            "愤怒", "生气", "恼火", "沮丧", "失望", "愤慨",
            "angry", "mad", "frustrated", "disappointed", "furious"
        ]
        score = 0.0
        
        content_lower = content.lower()
        for keyword in emotion_keywords:
            if keyword in content_lower:
                score += 0.25  # 增加权重
        
        # 语气检测 - 增加权重
        if "!" in content:
            score += 0.15
        if "？" in content and any(word in content_lower for word in ["为什么", "怎么", "why", "how"]):
            score += 0.1
        if content.isupper():
            score += 0.2
        
        # 特殊模式
        if any(pattern in content for pattern in ["从不", "总是", "never", "always"]):
            score += 0.2
        
        processing_time = time.time() - start_time
        return SignalResult("emotion", min(score, 1.0), 0.8, processing_time, datetime.now())
    
    async def _process_turn_taking(self, messages: List) -> SignalResult:
        """处理发言权检测"""
        start_time = time.time()
        
        if len(messages) < 3:
            return SignalResult("turn_taking", 0.0, 0.7, time.time() - start_time, datetime.now())
        
        # 检测重复发言
        recent_speakers = [msg.author_id for msg in messages[-3:]]
        unique_speakers = len(set(recent_speakers))
        
        # 如果同一人连续发言，分数增加
        score = 0.0
        if unique_speakers == 1:
            score = 0.4  # 增加分数
        elif unique_speakers == 2:
            score = 0.15
        
        processing_time = time.time() - start_time
        return SignalResult("turn_taking", score, 0.7, processing_time, datetime.now())
    
    async def _process_llm_score(self, context: List[str], message_data) -> SignalResult:
        """处理LLM评分"""
        start_time = time.time()
        
        score = await self.llm_processor.predictive_score(context)
        
        processing_time = time.time() - start_time
        return SignalResult("llm", score, 0.9, processing_time, datetime.now())

class OptimizedConflictMonitorFixed:
    """修复版本的优化冲突监控主类"""
    
    def __init__(self, api_key: str, api_base: str):
        self.signal_processor = ParallelSignalProcessorFixed(api_key, api_base)
        self.trigger_logic = IntelligentTriggerLogicFixed()
        self.performance_monitor = RealTimeMetrics()
        
    async def initialize(self):
        """初始化监控器"""
        await self.signal_processor.initialize()
        logger.info("🚀 优化的冲突监控系统已初始化")
    
    async def process_message(self, message_data) -> Tuple[bool, float, str, Dict]:
        """处理消息并返回干预决策"""
        start_time = time.time()
        
        try:
            # 并行处理所有信号
            signal_results = await self.signal_processor.process_signals_parallel(message_data)
            
            # 智能决策
            should_intervene, final_score, reason = self.trigger_logic.should_intervene(signal_results)
            
            # 更新性能指标
            processing_time = time.time() - start_time
            self.performance_monitor.total_processing_time = processing_time
            self.performance_monitor.avg_response_time = processing_time
            
            if should_intervene:
                self.performance_monitor.intervention_count += 1
            
            # 显示详细信号分数
            signal_details = {
                name: f"{result.value:.2f}" for name, result in signal_results.items()
            }
            
            logger.info(f"📊 处理完成: {processing_time:.3f}s, 分数: {final_score:.2f}, 干预: {should_intervene}")
            logger.info(f"🔍 信号详情: {signal_details}")
            
            return should_intervene, final_score, reason, signal_results
            
        except Exception as e:
            logger.error(f"❌ 消息处理失败: {e}")
            # 返回默认值
            return False, 0.0, f"处理失败: {e}", {}
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        return {
            "avg_response_time": self.performance_monitor.avg_response_time,
            "total_signals_processed": self.signal_processor.metrics.signal_count,
            "intervention_rate": (
                self.performance_monitor.intervention_count / 
                max(1, self.signal_processor.metrics.signal_count)
            ),
            "total_interventions": self.performance_monitor.intervention_count
        } 