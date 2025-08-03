"""
统一的干预生成器接口
"""

import asyncio
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

from .unified_mapping import UnifiedMapping, UnifiedTriggerType, UnifiedTKIStrategy
from .unified_detection_result import UnifiedDetectionResult

class UnifiedInterventionGenerator(ABC):
    """统一干预生成器接口"""
    
    def __init__(self):
        self.unified_mapping = UnifiedMapping()
    
    async def generate_intervention(
        self, 
        detection_result: UnifiedDetectionResult,
        admin_style: Optional[UnifiedTKIStrategy] = None
    ) -> str:
        """统一的干预生成方法"""
        
        # 使用统一映射获取策略
        if admin_style and admin_style != UnifiedTKIStrategy.AUTO:
            strategy = admin_style
        else:
            strategy = self.unified_mapping.get_strategy_for_trigger(
                detection_result.trigger_type, 
                detection_result.urgency_level
            )
        
        # 生成干预内容
        return await self._generate_by_strategy(strategy, detection_result)
    
    @abstractmethod
    async def _generate_by_strategy(
        self, 
        strategy: UnifiedTKIStrategy, 
        detection_result: UnifiedDetectionResult
    ) -> str:
        """根据策略生成干预内容（子类实现）"""
        pass

class GPTUnifiedInterventionGenerator(UnifiedInterventionGenerator):
    """GPT统一干预生成器实现"""
    
    def __init__(self):
        super().__init__()
        # 导入GPT风格干预生成器
        from ..interventions.gpt_style_intervention_generator import (
            GPTStyleInterventionGenerator, 
            GPTInterventionContext, 
            AdminInterventionStyle
        )
        self.gpt_generator = GPTStyleInterventionGenerator()
        
        # 策略映射
        self.strategy_mapping = {
            UnifiedTKIStrategy.COLLABORATING: AdminInterventionStyle.COLLABORATING,
            UnifiedTKIStrategy.ACCOMMODATING: AdminInterventionStyle.ACCOMMODATING,
            UnifiedTKIStrategy.COMPETING: AdminInterventionStyle.COMPETING,
            UnifiedTKIStrategy.COMPROMISING: AdminInterventionStyle.COMPROMISING,
            UnifiedTKIStrategy.AVOIDING: AdminInterventionStyle.AVOIDING,
            UnifiedTKIStrategy.AUTO: AdminInterventionStyle.AUTO
        }
    
    async def _generate_by_strategy(
        self, 
        strategy: UnifiedTKIStrategy, 
        detection_result: UnifiedDetectionResult
    ) -> str:
        """使用GPT生成器根据策略生成干预内容"""
        
        # 转换策略
        admin_style = self.strategy_mapping.get(strategy, AdminInterventionStyle.AUTO)
        
        # 创建GPT上下文
        context = GPTInterventionContext(
            trigger_type=self._convert_trigger_type(detection_result.trigger_type),
            urgency_level=detection_result.urgency_level,
            confidence=detection_result.confidence,
            recent_messages=detection_result.context.get('recent_messages', []),
            female_participants=detection_result.context.get('female_participants', []),
            male_participants=detection_result.context.get('male_participants', []),
            admin_style=admin_style
        )
        
        # 生成干预
        return await self.gpt_generator.generate_intervention(context)
    
    def _convert_trigger_type(self, unified_trigger: UnifiedTriggerType):
        """转换触发类型"""
        from ..interventions.gpt_style_intervention_generator import InterventionTrigger
        
        trigger_mapping = {
            UnifiedTriggerType.FEMALE_INTERRUPTED: InterventionTrigger.FEMALE_INTERRUPTED,
            UnifiedTriggerType.FEMALE_IGNORED: InterventionTrigger.FEMALE_IGNORED,
            UnifiedTriggerType.MALE_DOMINANCE: InterventionTrigger.MALE_DOMINANCE,
            UnifiedTriggerType.MALE_CONSECUTIVE: InterventionTrigger.MALE_CONSECUTIVE,
            UnifiedTriggerType.GENDER_IMBALANCE: InterventionTrigger.GENDER_IMBALANCE,
            UnifiedTriggerType.EXPRESSION_DIFFICULTY: InterventionTrigger.EXPRESSION_DIFFICULTY,
            UnifiedTriggerType.AGGRESSIVE_CONTEXT: InterventionTrigger.AGGRESSIVE_CONTEXT
        }
        
        return trigger_mapping.get(unified_trigger, InterventionTrigger.GENDER_IMBALANCE)

class TemplateUnifiedInterventionGenerator(UnifiedInterventionGenerator):
    """模板统一干预生成器实现"""
    
    def __init__(self):
        super().__init__()
        # 导入增强干预生成器
        from ..interventions.enhanced_intervention_generator import (
            EnhancedInterventionGenerator, 
            InterventionContext, 
            EnhancedInterventionTrigger,
            AdminInterventionStyle
        )
        self.template_generator = EnhancedInterventionGenerator()
        
        # 策略映射
        self.strategy_mapping = {
            UnifiedTKIStrategy.COLLABORATING: AdminInterventionStyle.COLLABORATING,
            UnifiedTKIStrategy.ACCOMMODATING: AdminInterventionStyle.ACCOMMODATING,
            UnifiedTKIStrategy.COMPETING: AdminInterventionStyle.COMPETING,
            UnifiedTKIStrategy.COMPROMISING: AdminInterventionStyle.COMPROMISING,
            UnifiedTKIStrategy.AVOIDING: AdminInterventionStyle.AVOIDING,
            UnifiedTKIStrategy.AUTO: AdminInterventionStyle.AUTO
        }
    
    async def _generate_by_strategy(
        self, 
        strategy: UnifiedTKIStrategy, 
        detection_result: UnifiedDetectionResult
    ) -> str:
        """使用模板生成器根据策略生成干预内容"""
        
        # 转换策略
        admin_style = self.strategy_mapping.get(strategy, AdminInterventionStyle.AUTO)
        
        # 转换触发类型
        trigger_type = self._convert_trigger_type(detection_result.trigger_type)
        
        # 创建模板上下文
        context = InterventionContext(
            trigger_type=trigger_type,
            urgency_level=detection_result.urgency_level,
            confidence=detection_result.confidence,
            recent_messages=detection_result.context.get('recent_messages', []),
            female_participants=detection_result.context.get('female_participants', []),
            male_participants=detection_result.context.get('male_participants', []),
            admin_style=admin_style
        )
        
        # 生成干预
        return self.template_generator.generate_intervention(context)
    
    def _convert_trigger_type(self, unified_trigger: UnifiedTriggerType):
        """转换触发类型"""
        from ..interventions.enhanced_intervention_generator import EnhancedInterventionTrigger
        
        trigger_mapping = {
            UnifiedTriggerType.FEMALE_INTERRUPTED: EnhancedInterventionTrigger.FEMALE_INTERRUPTED,
            UnifiedTriggerType.FEMALE_IGNORED: EnhancedInterventionTrigger.FEMALE_IGNORED,
            UnifiedTriggerType.MALE_DOMINANCE: EnhancedInterventionTrigger.MALE_DOMINANCE,
            UnifiedTriggerType.MALE_CONSECUTIVE: EnhancedInterventionTrigger.MALE_CONSECUTIVE,
            UnifiedTriggerType.GENDER_IMBALANCE: EnhancedInterventionTrigger.GENDER_IMBALANCE,
            UnifiedTriggerType.EXPRESSION_DIFFICULTY: EnhancedInterventionTrigger.EXPRESSION_DIFFICULTY,
            UnifiedTriggerType.AGGRESSIVE_CONTEXT: EnhancedInterventionTrigger.AGGRESSIVE_CONTEXT
        }
        
        return trigger_mapping.get(unified_trigger, EnhancedInterventionTrigger.GENDER_IMBALANCE) 