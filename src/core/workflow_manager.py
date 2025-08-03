"""
工作流管理器 - 整合检测器和GPT提示生成器
实现完整的工作流：检测时机 → 选择策略 → 生成GPT提示 → 获取插话内容
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from detectors.when_to_interrupt import WhenToInterruptDetector, InterruptionDecision
from interventions.tki_gender_aware_intervention import TKIGenderAwareInterventionGenerator, TKIStrategy
from interventions.gpt_prompt_generator import GPTPromptGenerator, ConversationContext, TriggerType
from core.unified_mapping import UnifiedMapping, UnifiedTKIStrategy

@dataclass
class WorkflowResult:
    """工作流结果"""
    should_intervene: bool
    trigger_type: Optional[str] = None
    strategy: Optional[str] = None
    gpt_prompt: Optional[str] = None
    suggested_intervention: Optional[str] = None
    confidence: float = 0.0
    reasoning: Optional[str] = None
    context_messages: List[Dict[str, str]] = None

class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self):
        self.detector = WhenToInterruptDetector()
        self.intervention_generator = TKIGenderAwareInterventionGenerator()
        self.prompt_generator = GPTPromptGenerator()
        self.unified_mapping = UnifiedMapping()
        self.conversation_history = []
        
    async def process_message(self, 
                            message: str, 
                            author: str, 
                            gender: str,
                            timestamp: datetime = None) -> WorkflowResult:
        """处理消息，执行完整工作流"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # 更新对话历史
        self._update_conversation_history(message, author, gender, timestamp)
        
        # 步骤1：检测是否需要插话
        detection_result = self.detector.analyze_message(message, author, gender, timestamp)
        
        if not detection_result.should_interrupt:
            return WorkflowResult(
                should_intervene=False,
                reasoning=detection_result.reasoning,
                context_messages=self._get_recent_messages(5)
            )
        
        # 步骤2：使用统一映射选择TKI策略
        unified_trigger = self.unified_mapping.convert_detector_trigger(detection_result.trigger_type.value)
        strategy = self.unified_mapping.get_strategy_for_trigger(unified_trigger, detection_result.urgency_level)
        
        # 步骤3：生成GPT提示
        context = self._create_conversation_context(detection_result, strategy)
        gpt_prompt = self.prompt_generator.generate_prompt(context)
        
        # 步骤4：生成建议的干预内容（这里可以调用GPT API）
        suggested_intervention = await self._generate_intervention_with_gpt(gpt_prompt)
        
        return WorkflowResult(
            should_intervene=True,
            trigger_type=unified_trigger,
            strategy=strategy.value,
            gpt_prompt=gpt_prompt,
            suggested_intervention=suggested_intervention,
            confidence=detection_result.confidence,
            reasoning=detection_result.reasoning,
            context_messages=self._get_recent_messages(5)
        )
    
    def _update_conversation_history(self, message: str, author: str, gender: str, timestamp: datetime):
        """更新对话历史"""
        self.conversation_history.append({
            'message': message,
            'author': author,
            'gender': gender,
            'timestamp': timestamp
        })
        
        # 保持最近50条消息
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def _get_recent_messages(self, count: int = 5) -> List[Dict[str, str]]:
        """获取最近的消息"""
        recent = self.conversation_history[-count:] if len(self.conversation_history) >= count else self.conversation_history
        return [
            {
                'speaker': msg['author'],
                'message': msg['message']
            }
            for msg in recent
        ]
    
    def _create_conversation_context(self, 
                                   detection_result: InterruptionDecision, 
                                   strategy: UnifiedTKIStrategy) -> ConversationContext:
        """创建对话上下文"""
        
        recent_messages = self._get_recent_messages(5)
        
        # 识别女性发言者和男性发言者
        female_speaker = None
        male_speakers = []
        
        for msg in recent_messages:
            # 这里需要根据实际数据获取性别信息
            # 暂时使用简单的启发式方法
            if 'Lily' in msg['speaker'] or 'female' in msg['speaker'].lower():
                female_speaker = msg['speaker']
            elif any(name in msg['speaker'] for name in ['Alex', 'Zack', 'male']):
                male_speakers.append(msg['speaker'])
        
        # 转换触发类型到GPT提示生成器格式
        unified_trigger = self.unified_mapping.convert_detector_trigger(detection_result.trigger_type.value)
        gpt_trigger = self._convert_to_gpt_trigger(unified_trigger)
        
        return self.prompt_generator.create_context_from_detection(
            recent_messages=recent_messages,
            trigger_type=gpt_trigger,
            strategy=strategy.value,
            female_speaker=female_speaker,
            male_speakers=male_speakers
        )
    
    def _convert_to_gpt_trigger(self, unified_trigger: str) -> str:
        """转换统一触发类型到GPT提示生成器格式"""
        # 反向映射：统一格式到GPT格式
        unified_to_gpt = {
            'female_interrupted': '❸',
            'female_ignored': '❷',
            'male_dominance': '❶',
            'expression_difficulty': '❹',
            'aggressive_context': '❺'
        }
        return unified_to_gpt.get(unified_trigger, '❷')
    
    async def _generate_intervention_with_gpt(self, prompt: str) -> str:
        """使用GPT生成干预内容"""
        # 这里应该调用实际的GPT API
        # 暂时返回一个示例响应
        
        # 模拟GPT响应
        sample_responses = [
            "Let's hear from everyone to get a complete picture.",
            "Maybe we can take turns sharing opinions?",
            "Everyone deserves a chance to speak.",
            "Let's consider all perspectives here.",
            "Your thoughts are important to us."
        ]
        
        # 根据prompt内容选择合适的响应
        if "interrupted" in prompt.lower():
            return "Let's let her finish—everyone deserves a chance to speak."
        elif "ignored" in prompt.lower():
            return "Maybe we can take turns sharing opinions? Her point was interesting."
        elif "dominating" in prompt.lower():
            return "Both perspectives are valuable. Let's hear from everyone."
        else:
            return sample_responses[0]
    
    def get_workflow_status(self) -> Dict:
        """获取工作流状态"""
        return {
            "conversation_history_length": len(self.conversation_history),
            "detector_status": "active",
            "intervention_generator_status": "active",
            "prompt_generator_status": "active",
            "unified_mapping_status": "active",
            "last_processed_time": datetime.now().isoformat()
        }
    
    def get_trigger_type_mapping(self) -> Dict:
        """获取触发类型映射"""
        return self.unified_mapping.get_all_mappings()
    
    def get_strategy_mapping(self) -> Dict:
        """获取策略映射"""
        return {
            "collaborating": "协作型 - 整合观点，推动共识",
            "accommodating": "迁就型 - 优先和谐，温和支持",
            "competing": "竞争型 - 强势捍卫女性表达权",
            "compromising": "妥协型 - 设置公平讨论机制",
            "avoiding": "回避型 - 岔开矛盾话题"
        }
    
    def get_unified_mapping_info(self) -> Dict:
        """获取统一映射信息"""
        return {
            "total_triggers": len(self.unified_mapping.trigger_strategy_mappings),
            "total_strategies": len(UnifiedTKIStrategy),
            "mappings": self.unified_mapping.get_all_mappings()
        } 