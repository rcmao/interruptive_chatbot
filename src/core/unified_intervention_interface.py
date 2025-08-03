"""
统一的干预生成器接口
为所有干预生成器提供标准化的接口，确保一致性和可扩展性
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .unified_detection_result import UnifiedDetectionResult
from .unified_mapping import UnifiedTKIStrategy

class GeneratorType(Enum):
    """生成器类型"""
    COMPREHENSIVE = "comprehensive"      # 综合干预生成器
    GPT_STYLE = "gpt_style"             # GPT风格生成器
    TKI_GENDER_AWARE = "tki_gender_aware"  # TKI性别意识生成器
    TEMPLATE_BASED = "template_based"   # 模板基础生成器
    PROMPT_BASED = "prompt_based"       # 提示基础生成器

@dataclass
class GeneratorConfig:
    """生成器配置"""
    generator_type: GeneratorType
    enabled: bool = True
    priority: int = 1  # 1-10，数字越大优先级越高
    timeout: float = 10.0  # 超时时间（秒）
    weight: float = 1.0  # 权重，用于结果选择

@dataclass
class InterventionContext:
    """干预上下文"""
    detection_result: UnifiedDetectionResult
    conversation_context: Dict
    admin_style: Optional[UnifiedTKIStrategy] = None
    room_id: Optional[str] = None
    participants: Optional[Dict] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class UnifiedInterventionGenerator(ABC):
    """统一干预生成器接口"""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def generate_intervention(self, context: InterventionContext) -> str:
        """
        生成干预内容
        
        Args:
            context: 干预上下文
            
        Returns:
            str: 生成的干预内容
        """
        pass
    
    @abstractmethod
    def get_generator_info(self) -> Dict:
        """获取生成器信息"""
        pass
    
    def is_enabled(self) -> bool:
        """检查生成器是否启用"""
        return self.config.enabled
    
    def get_priority(self) -> int:
        """获取生成器优先级"""
        return self.config.priority
    
    def get_weight(self) -> float:
        """获取生成器权重"""
        return self.config.weight
    
    def can_handle_trigger_type(self, trigger_type) -> bool:
        """检查是否能处理指定的触发类型"""
        return True  # 默认实现，子类可以重写

class GeneratorResult:
    """生成器结果包装器"""
    
    def __init__(self, generator: UnifiedInterventionGenerator, 
                 intervention: str, processing_time: float):
        self.generator = generator
        self.intervention = intervention
        self.processing_time = processing_time
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'generator_name': self.generator.name,
            'generator_type': self.generator.config.generator_type.value,
            'intervention': self.intervention,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.generator.get_priority(),
            'weight': self.generator.get_weight()
        }

class GeneratorRegistry:
    """生成器注册表"""
    
    def __init__(self):
        self._generators: Dict[str, UnifiedInterventionGenerator] = {}
        self._configs: Dict[str, GeneratorConfig] = {}
    
    def register_generator(self, generator: UnifiedInterventionGenerator):
        """注册生成器"""
        self._generators[generator.name] = generator
        self._configs[generator.name] = generator.config
    
    def unregister_generator(self, generator_name: str):
        """注销生成器"""
        if generator_name in self._generators:
            del self._generators[generator_name]
            del self._configs[generator_name]
    
    def get_generator(self, generator_name: str) -> Optional[UnifiedInterventionGenerator]:
        """获取生成器"""
        return self._generators.get(generator_name)
    
    def get_enabled_generators(self) -> List[UnifiedInterventionGenerator]:
        """获取所有启用的生成器"""
        return [generator for generator in self._generators.values() 
                if generator.is_enabled()]
    
    def get_generators_by_priority(self) -> List[UnifiedInterventionGenerator]:
        """按优先级排序获取生成器"""
        enabled_generators = self.get_enabled_generators()
        return sorted(enabled_generators, key=lambda g: g.get_priority(), reverse=True)
    
    def get_generators_for_trigger(self, trigger_type) -> List[UnifiedInterventionGenerator]:
        """获取能处理指定触发类型的生成器"""
        enabled_generators = self.get_enabled_generators()
        return [g for g in enabled_generators if g.can_handle_trigger_type(trigger_type)]
    
    def get_generator_configs(self) -> Dict[str, GeneratorConfig]:
        """获取所有生成器配置"""
        return self._configs.copy()
    
    def update_generator_config(self, generator_name: str, config: GeneratorConfig):
        """更新生成器配置"""
        if generator_name in self._generators:
            self._generators[generator_name].config = config
            self._configs[generator_name] = config

class InterventionManager:
    """干预管理器"""
    
    def __init__(self):
        self.registry = GeneratorRegistry()
        self.intervention_cache = {}  # 简单的干预缓存
    
    def register_generator(self, generator: UnifiedInterventionGenerator):
        """注册生成器"""
        self.registry.register_generator(generator)
    
    async def generate_intervention(self, detection_result: UnifiedDetectionResult,
                                  context: Dict, admin_style: Optional[UnifiedTKIStrategy] = None) -> Optional[str]:
        """
        生成干预内容
        
        Args:
            detection_result: 检测结果
            context: 对话上下文
            admin_style: 管理员设置的风格
            
        Returns:
            Optional[str]: 生成的干预内容，如果不需要干预则返回None
        """
        if not detection_result.should_intervene:
            return None
        
        # 创建干预上下文
        intervention_context = InterventionContext(
            detection_result=detection_result,
            conversation_context=context,
            admin_style=admin_style
        )
        
        # 获取能处理该触发类型的生成器
        generators = self.registry.get_generators_for_trigger(detection_result.trigger_type)
        
        if not generators:
            # 如果没有专门的生成器，使用所有启用的生成器
            generators = self.registry.get_enabled_generators()
        
        if not generators:
            return None
        
        # 运行生成器
        generator_results = await self._run_generators(generators, intervention_context)
        
        if not generator_results:
            return None
        
        # 选择最佳结果
        best_result = self._select_best_result(generator_results, detection_result)
        
        return best_result.intervention if best_result else None
    
    async def _run_generators(self, generators: List[UnifiedInterventionGenerator],
                            context: InterventionContext) -> List[GeneratorResult]:
        """运行生成器"""
        import asyncio
        import time
        
        # 创建生成任务
        tasks = []
        for generator in generators:
            task = self._run_single_generator(generator, context)
            tasks.append(task)
        
        # 并行执行所有生成器
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        generator_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 记录错误但继续处理其他结果
                print(f"生成器 {generators[i].name} 执行失败: {result}")
                continue
            
            if result is not None:
                generator_results.append(result)
        
        return generator_results
    
    async def _run_single_generator(self, generator: UnifiedInterventionGenerator,
                                  context: InterventionContext) -> Optional[GeneratorResult]:
        """运行单个生成器"""
        import asyncio
        import time
        
        start_time = time.time()
        
        try:
            # 设置超时
            intervention = await asyncio.wait_for(
                generator.generate_intervention(context),
                timeout=generator.config.timeout
            )
            
            processing_time = time.time() - start_time
            
            return GeneratorResult(generator, intervention, processing_time)
            
        except asyncio.TimeoutError:
            print(f"生成器 {generator.name} 超时")
            return None
        except Exception as e:
            print(f"生成器 {generator.name} 执行错误: {e}")
            return None
    
    def _select_best_result(self, generator_results: List[GeneratorResult],
                          detection_result: UnifiedDetectionResult) -> Optional[GeneratorResult]:
        """
        选择最佳生成结果
        
        策略：
        1. 优先选择处理时间短的结果
        2. 考虑生成器权重
        3. 考虑检测结果的紧急程度
        """
        if not generator_results:
            return None
        
        # 计算综合分数
        best_result = None
        best_score = 0.0
        
        for generator_result in generator_results:
            generator = generator_result.generator
            
            # 综合分数 = 权重 * (1 / 处理时间) * 紧急程度系数
            urgency_factor = detection_result.urgency_level / 5.0
            time_factor = 1.0 / max(generator_result.processing_time, 0.1)  # 避免除零
            score = generator.get_weight() * time_factor * urgency_factor
            
            if score > best_score:
                best_score = score
                best_result = generator_result
        
        return best_result
    
    def get_intervention_summary(self) -> Dict:
        """获取干预摘要"""
        generators = self.registry.get_enabled_generators()
        
        return {
            'total_generators': len(generators),
            'generator_types': [g.config.generator_type.value for g in generators],
            'generator_names': [g.name for g in generators],
            'configs': self.registry.get_generator_configs()
        } 