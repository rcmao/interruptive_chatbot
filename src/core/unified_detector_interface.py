"""
统一的检测器接口
为所有检测器提供标准化的接口，确保一致性和可扩展性
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .unified_detection_result import UnifiedDetectionResult
from .unified_mapping import UnifiedTriggerType

class DetectorType(Enum):
    """检测器类型"""
    ENHANCED_INTERRUPTION = "enhanced_interruption"
    GENDER_BASED = "gender_based"
    CONTEXT_AWARE = "context_aware"
    ULTRA_FAST = "ultra_fast"
    TEAM_COLLABORATION = "team_collaboration"
    GPT_REALTIME = "gpt_realtime"

@dataclass
class DetectorConfig:
    """检测器配置"""
    detector_type: DetectorType
    enabled: bool = True
    priority: int = 1  # 1-10，数字越大优先级越高
    timeout: float = 5.0  # 超时时间（秒）
    weight: float = 1.0  # 权重，用于结果合并

class UnifiedDetector(ABC):
    """统一检测器接口"""
    
    def __init__(self, config: DetectorConfig):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def detect(self, message: str, author: str, gender: str, 
                    context: List[Dict]) -> UnifiedDetectionResult:
        """
        执行检测
        
        Args:
            message: 当前消息
            author: 消息作者
            gender: 作者性别
            context: 对话上下文
            
        Returns:
            UnifiedDetectionResult: 统一的检测结果
        """
        pass
    
    @abstractmethod
    def get_detector_info(self) -> Dict:
        """获取检测器信息"""
        pass
    
    def is_enabled(self) -> bool:
        """检查检测器是否启用"""
        return self.config.enabled
    
    def get_priority(self) -> int:
        """获取检测器优先级"""
        return self.config.priority
    
    def get_weight(self) -> float:
        """获取检测器权重"""
        return self.config.weight

class DetectorResult:
    """检测器结果包装器"""
    
    def __init__(self, detector: UnifiedDetector, result: UnifiedDetectionResult, 
                 processing_time: float):
        self.detector = detector
        self.result = result
        self.processing_time = processing_time
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'detector_name': self.detector.name,
            'detector_type': self.detector.config.detector_type.value,
            'result': self.result.to_dict(),
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.detector.get_priority(),
            'weight': self.detector.get_weight()
        }

class DetectorRegistry:
    """检测器注册表"""
    
    def __init__(self):
        self._detectors: Dict[str, UnifiedDetector] = {}
        self._configs: Dict[str, DetectorConfig] = {}
    
    def register_detector(self, detector: UnifiedDetector):
        """注册检测器"""
        self._detectors[detector.name] = detector
        self._configs[detector.name] = detector.config
    
    def unregister_detector(self, detector_name: str):
        """注销检测器"""
        if detector_name in self._detectors:
            del self._detectors[detector_name]
            del self._configs[detector_name]
    
    def get_detector(self, detector_name: str) -> Optional[UnifiedDetector]:
        """获取检测器"""
        return self._detectors.get(detector_name)
    
    def get_enabled_detectors(self) -> List[UnifiedDetector]:
        """获取所有启用的检测器"""
        return [detector for detector in self._detectors.values() 
                if detector.is_enabled()]
    
    def get_detectors_by_priority(self) -> List[UnifiedDetector]:
        """按优先级排序获取检测器"""
        enabled_detectors = self.get_enabled_detectors()
        return sorted(enabled_detectors, key=lambda d: d.get_priority(), reverse=True)
    
    def get_detector_configs(self) -> Dict[str, DetectorConfig]:
        """获取所有检测器配置"""
        return self._configs.copy()
    
    def update_detector_config(self, detector_name: str, config: DetectorConfig):
        """更新检测器配置"""
        if detector_name in self._detectors:
            self._detectors[detector_name].config = config
            self._configs[detector_name] = config

class DetectorManager:
    """检测器管理器"""
    
    def __init__(self):
        self.registry = DetectorRegistry()
        self.result_cache = {}  # 简单的结果缓存
    
    def register_detector(self, detector: UnifiedDetector):
        """注册检测器"""
        self.registry.register_detector(detector)
    
    async def run_detection(self, message: str, author: str, gender: str, 
                          context: List[Dict]) -> List[DetectorResult]:
        """
        运行所有启用的检测器
        
        Returns:
            List[DetectorResult]: 所有检测器的结果
        """
        import asyncio
        import time
        
        detectors = self.registry.get_enabled_detectors()
        if not detectors:
            return []
        
        # 创建检测任务
        tasks = []
        for detector in detectors:
            task = self._run_single_detector(detector, message, author, gender, context)
            tasks.append(task)
        
        # 并行执行所有检测器
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        detector_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 记录错误但继续处理其他结果
                print(f"检测器 {detectors[i].name} 执行失败: {result}")
                continue
            
            if result is not None:
                detector_results.append(result)
        
        return detector_results
    
    async def _run_single_detector(self, detector: UnifiedDetector, 
                                 message: str, author: str, gender: str, 
                                 context: List[Dict]) -> Optional[DetectorResult]:
        """运行单个检测器"""
        import asyncio
        import time
        
        start_time = time.time()
        
        try:
            # 设置超时
            result = await asyncio.wait_for(
                detector.detect(message, author, gender, context),
                timeout=detector.config.timeout
            )
            
            processing_time = time.time() - start_time
            
            return DetectorResult(detector, result, processing_time)
            
        except asyncio.TimeoutError:
            print(f"检测器 {detector.name} 超时")
            return None
        except Exception as e:
            print(f"检测器 {detector.name} 执行错误: {e}")
            return None
    
    def select_best_result(self, detector_results: List[DetectorResult]) -> Optional[UnifiedDetectionResult]:
        """
        选择最佳检测结果
        
        策略：
        1. 优先选择置信度高的结果
        2. 考虑检测器权重
        3. 考虑紧急程度
        """
        if not detector_results:
            return None
        
        # 过滤出需要干预的结果
        intervention_results = [r for r in detector_results if r.result.should_intervene]
        
        if not intervention_results:
            return None
        
        # 计算综合分数
        best_result = None
        best_score = 0.0
        
        for detector_result in intervention_results:
            result = detector_result.result
            detector = detector_result.detector
            
            # 综合分数 = 置信度 * 权重 * 紧急程度系数
            urgency_factor = result.urgency_level / 5.0
            score = result.confidence * detector.get_weight() * urgency_factor
            
            if score > best_score:
                best_score = score
                best_result = result
        
        return best_result
    
    def get_detection_summary(self) -> Dict:
        """获取检测摘要"""
        detectors = self.registry.get_enabled_detectors()
        
        return {
            'total_detectors': len(detectors),
            'detector_types': [d.config.detector_type.value for d in detectors],
            'detector_names': [d.name for d in detectors],
            'configs': self.registry.get_detector_configs()
        } 