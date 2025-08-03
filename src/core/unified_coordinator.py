"""
统一的打断协调器
整合检测器和干预生成器，提供完整的打断处理流程
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from .unified_detection_result import UnifiedDetectionResult
from .unified_intervention_interface import InterventionContext
from .unified_mapping import UnifiedTKIStrategy, UnifiedMapping
from .unified_detector_interface import DetectorManager, DetectorResult
from .unified_intervention_interface import InterventionManager, GeneratorResult

logger = logging.getLogger(__name__)

@dataclass
class CoordinationResult:
    """协调结果"""
    should_intervene: bool
    intervention_message: Optional[str] = None
    detection_result: Optional[UnifiedDetectionResult] = None
    processing_time: float = 0.0
    detector_results: List[DetectorResult] = None
    generator_results: List[GeneratorResult] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.detector_results is None:
            self.detector_results = []
        if self.generator_results is None:
            self.generator_results = []

class UnifiedInterruptionCoordinator:
    """统一的打断协调器"""
    
    def __init__(self):
        self.detector_manager = DetectorManager()
        self.intervention_manager = InterventionManager()
        self.unified_mapping = UnifiedMapping()
        
        # 配置参数
        self.config = {
            'enable_parallel_processing': True,
            'enable_caching': True,
            'cache_ttl': 300,  # 缓存生存时间（秒）
            'max_processing_time': 30.0,  # 最大处理时间（秒）
            'cooldown_period': 30,  # 冷却期（秒）
        }
        
        # 状态跟踪
        self.last_intervention_time = None
        self.intervention_count = 0
        self.total_messages_processed = 0
        
        # 缓存
        self._detection_cache = {}
        self._intervention_cache = {}
    
    def register_detector(self, detector):
        """注册检测器"""
        self.detector_manager.register_detector(detector)
        logger.info(f"注册检测器: {detector.name}")
    
    def register_generator(self, generator):
        """注册干预生成器"""
        self.intervention_manager.register_generator(generator)
        logger.info(f"注册干预生成器: {generator.name}")
    
    async def process_message(self, message: str, author: str, gender: str, 
                            context: List[Dict], admin_style: Optional[UnifiedTKIStrategy] = None,
                            room_id: Optional[str] = None) -> CoordinationResult:
        """
        处理消息，决定是否需要干预
        
        Args:
            message: 当前消息
            author: 消息作者
            gender: 作者性别
            context: 对话上下文
            admin_style: 管理员设置的风格
            room_id: 房间ID
            
        Returns:
            CoordinationResult: 协调结果
        """
        import time
        start_time = time.time()
        
        try:
            # 更新统计
            self.total_messages_processed += 1
            
            # 检查冷却期
            if self._is_in_cooldown():
                return CoordinationResult(
                    should_intervene=False,
                    processing_time=time.time() - start_time,
                    detector_results=[],
                    generator_results=[]
                )
            
            # 检查缓存
            cache_key = self._generate_cache_key(message, author, gender, context)
            if self.config['enable_caching'] and cache_key in self._detection_cache:
                cached_result = self._detection_cache[cache_key]
                if self._is_cache_valid(cached_result['timestamp']):
                    logger.debug(f"使用缓存的检测结果: {cache_key}")
                    return cached_result['result']
            
            # 1. 运行检测器
            detector_results = await self.detector_manager.run_detection(
                message, author, gender, context
            )
            
            # 2. 选择最佳检测结果
            best_detection = self.detector_manager.select_best_result(detector_results)
            
            if not best_detection or not best_detection.should_intervene:
                result = CoordinationResult(
                    should_intervene=False,
                    processing_time=time.time() - start_time,
                    detector_results=detector_results,
                    generator_results=[]
                )
                
                # 缓存结果
                if self.config['enable_caching']:
                    self._cache_result(cache_key, result)
                
                return result
            
            # 3. 生成干预内容
            intervention_message = await self.intervention_manager.generate_intervention(
                best_detection, context, admin_style
            )
            
            # 4. 创建协调结果
            result = CoordinationResult(
                should_intervene=True,
                intervention_message=intervention_message,
                detection_result=best_detection,
                processing_time=time.time() - start_time,
                detector_results=detector_results,
                generator_results=[]  # 这里可以添加生成器结果
            )
            
            # 更新干预统计
            if intervention_message:
                self.intervention_count += 1
                self.last_intervention_time = datetime.now()
            
            # 缓存结果
            if self.config['enable_caching']:
                self._cache_result(cache_key, result)
            
            logger.info(f"生成干预: {intervention_message[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
            return CoordinationResult(
                should_intervene=False,
                processing_time=time.time() - start_time,
                detector_results=[],
                generator_results=[]
            )
    
    def _is_in_cooldown(self) -> bool:
        """检查是否在冷却期内"""
        if self.last_intervention_time is None:
            return False
        
        time_since_last = datetime.now() - self.last_intervention_time
        return time_since_last.total_seconds() < self.config['cooldown_period']
    
    def _generate_cache_key(self, message: str, author: str, gender: str, context: List[Dict]) -> str:
        """生成缓存键"""
        import hashlib
        
        # 创建缓存键的内容
        content = f"{message}:{author}:{gender}:{len(context)}"
        
        # 添加上下文的简要信息
        if context:
            recent_messages = context[-3:]  # 只考虑最近3条消息
            context_summary = "".join([msg.get('author', '') + msg.get('message', '')[:20] 
                                     for msg in recent_messages])
            content += f":{context_summary}"
        
        # 生成哈希
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """检查缓存是否有效"""
        time_since_cache = datetime.now() - timestamp
        return time_since_cache.total_seconds() < self.config['cache_ttl']
    
    def _cache_result(self, cache_key: str, result: CoordinationResult):
        """缓存结果"""
        self._detection_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        # 清理过期缓存
        self._cleanup_cache()
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, value in self._detection_cache.items():
            if not self._is_cache_valid(value['timestamp']):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._detection_cache[key]
        
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存")
    
    def get_coordination_summary(self) -> Dict:
        """获取协调摘要"""
        return {
            'total_messages_processed': self.total_messages_processed,
            'intervention_count': self.intervention_count,
            'intervention_rate': self.intervention_count / max(self.total_messages_processed, 1),
            'last_intervention': self.last_intervention_time.isoformat() if self.last_intervention_time else None,
            'cooldown_active': self._is_in_cooldown(),
            'cache_size': len(self._detection_cache),
            'detector_summary': self.detector_manager.get_detection_summary(),
            'intervention_summary': self.intervention_manager.get_intervention_summary(),
            'config': self.config
        }
    
    def update_config(self, new_config: Dict):
        """更新配置"""
        self.config.update(new_config)
        logger.info(f"更新协调器配置: {new_config}")
    
    def reset_statistics(self):
        """重置统计信息"""
        self.intervention_count = 0
        self.total_messages_processed = 0
        self.last_intervention_time = None
        self._detection_cache.clear()
        self._intervention_cache.clear()
        logger.info("重置协调器统计信息")
    
    def get_detector_performance(self) -> Dict:
        """获取检测器性能统计"""
        detector_results = []
        
        for detector in self.detector_manager.registry.get_enabled_detectors():
            detector_info = detector.get_detector_info()
            detector_info.update({
                'name': detector.name,
                'type': detector.config.detector_type.value,
                'enabled': detector.is_enabled(),
                'priority': detector.get_priority(),
                'weight': detector.get_weight()
            })
            detector_results.append(detector_info)
        
        return {
            'detectors': detector_results,
            'total_enabled': len([d for d in detector_results if d['enabled']])
        }
    
    def get_generator_performance(self) -> Dict:
        """获取生成器性能统计"""
        generator_results = []
        
        for generator in self.intervention_manager.registry.get_enabled_generators():
            generator_info = generator.get_generator_info()
            generator_info.update({
                'name': generator.name,
                'type': generator.config.generator_type.value,
                'enabled': generator.is_enabled(),
                'priority': generator.get_priority(),
                'weight': generator.get_weight()
            })
            generator_results.append(generator_info)
        
        return {
            'generators': generator_results,
            'total_enabled': len([g for g in generator_results if g['enabled']])
        }

# 全局协调器实例
_global_coordinator = None

def get_global_coordinator() -> UnifiedInterruptionCoordinator:
    """获取全局协调器实例"""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = UnifiedInterruptionCoordinator()
    return _global_coordinator

def set_global_coordinator(coordinator: UnifiedInterruptionCoordinator):
    """设置全局协调器实例"""
    global _global_coordinator
    _global_coordinator = coordinator 