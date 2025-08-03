"""
统一映射 - 确保detectors和interventions之间的逻辑一致性
提供统一的触发类型映射和策略选择逻辑
"""

from enum import Enum
from typing import Dict, List, Optional

class UnifiedTriggerType(Enum):
    """统一的触发类型"""
    FEMALE_INTERRUPTED = "female_interrupted"      # 女性被打断
    FEMALE_IGNORED = "female_ignored"              # 女性被忽视
    MALE_DOMINANCE = "male_dominance"              # 男性主导对话
    MALE_CONSECUTIVE = "male_consecutive"          # 男性连续发言
    GENDER_IMBALANCE = "gender_imbalance"          # 性别不平衡
    EXPRESSION_DIFFICULTY = "expression_difficulty"  # 表达困难
    AGGRESSIVE_CONTEXT = "aggressive_context"      # 攻击性语境

class UnifiedTKIStrategy(Enum):
    """统一的TKI策略"""
    COLLABORATING = "collaborating"    # 协作型
    ACCOMMODATING = "accommodating"    # 迁就型
    COMPETING = "competing"            # 竞争型
    COMPROMISING = "compromising"      # 妥协型
    AVOIDING = "avoiding"              # 回避型
    AUTO = "auto"                      # 自动选择

class UnifiedMapping:
    """统一映射管理器"""
    
    def __init__(self):
        self.trigger_mappings = self._initialize_trigger_mappings()
        self.strategy_mappings = self._initialize_strategy_mappings()
        self.urgency_mappings = self._initialize_urgency_mappings()
    
    def _initialize_trigger_mappings(self) -> Dict[str, UnifiedTriggerType]:
        """初始化触发类型映射"""
        return {
            # Enhanced Interruption Detector 映射
            "female_interrupted": UnifiedTriggerType.FEMALE_INTERRUPTED,
            "female_ignored": UnifiedTriggerType.FEMALE_IGNORED,
            "male_dominance": UnifiedTriggerType.MALE_DOMINANCE,
            "male_consecutive": UnifiedTriggerType.MALE_CONSECUTIVE,
            "gender_imbalance": UnifiedTriggerType.GENDER_IMBALANCE,
            "expression_difficulty": UnifiedTriggerType.EXPRESSION_DIFFICULTY,
            "aggressive_context": UnifiedTriggerType.AGGRESSIVE_CONTEXT,
            
            # Gender Based Interruption Detector 映射
            "structural_marginalization": UnifiedTriggerType.FEMALE_INTERRUPTED,
            "potential_aggression": UnifiedTriggerType.AGGRESSIVE_CONTEXT,
            
            # When To Interrupt Detector 映射
            "conversation_dominance": UnifiedTriggerType.MALE_DOMINANCE,
            "silence_after_female": UnifiedTriggerType.FEMALE_IGNORED,
        }
    
    def _initialize_strategy_mappings(self) -> Dict[UnifiedTriggerType, Dict[int, UnifiedTKIStrategy]]:
        """初始化策略映射（根据触发类型和紧急程度）"""
        return {
            UnifiedTriggerType.FEMALE_INTERRUPTED: {
                5: UnifiedTKIStrategy.COMPETING,    # 高紧急 - 竞争型
                4: UnifiedTKIStrategy.COMPETING,    # 中高紧急 - 竞争型
                3: UnifiedTKIStrategy.COMPROMISING, # 中等紧急 - 妥协型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            },
            UnifiedTriggerType.AGGRESSIVE_CONTEXT: {
                5: UnifiedTKIStrategy.COMPETING,    # 高紧急 - 竞争型
                4: UnifiedTKIStrategy.COMPETING,    # 中高紧急 - 竞争型
                3: UnifiedTKIStrategy.COMPROMISING, # 中等紧急 - 妥协型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            },
            UnifiedTriggerType.MALE_DOMINANCE: {
                5: UnifiedTKIStrategy.COMPETING,    # 高紧急 - 竞争型
                4: UnifiedTKIStrategy.COLLABORATING, # 中高紧急 - 协作型
                3: UnifiedTKIStrategy.COMPROMISING, # 中等紧急 - 妥协型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            },
            UnifiedTriggerType.MALE_CONSECUTIVE: {
                5: UnifiedTKIStrategy.COLLABORATING, # 高紧急 - 协作型
                4: UnifiedTKIStrategy.COLLABORATING, # 中高紧急 - 协作型
                3: UnifiedTKIStrategy.COMPROMISING, # 中等紧急 - 妥协型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            },
            UnifiedTriggerType.FEMALE_IGNORED: {
                5: UnifiedTKIStrategy.COMPROMISING, # 高紧急 - 妥协型
                4: UnifiedTKIStrategy.COMPROMISING, # 中高紧急 - 妥协型
                3: UnifiedTKIStrategy.COLLABORATING, # 中等紧急 - 协作型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            },
            UnifiedTriggerType.EXPRESSION_DIFFICULTY: {
                5: UnifiedTKIStrategy.ACCOMMODATING, # 高紧急 - 迁就型
                4: UnifiedTKIStrategy.ACCOMMODATING, # 中高紧急 - 迁就型
                3: UnifiedTKIStrategy.COLLABORATING, # 中等紧急 - 协作型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            },
            UnifiedTriggerType.GENDER_IMBALANCE: {
                5: UnifiedTKIStrategy.COMPROMISING, # 高紧急 - 妥协型
                4: UnifiedTKIStrategy.COMPROMISING, # 中高紧急 - 妥协型
                3: UnifiedTKIStrategy.COLLABORATING, # 中等紧急 - 协作型
                2: UnifiedTKIStrategy.COLLABORATING, # 低紧急 - 协作型
                1: UnifiedTKIStrategy.ACCOMMODATING # 很低紧急 - 迁就型
            }
        }
    
    def _initialize_urgency_mappings(self) -> Dict[str, int]:
        """初始化紧急程度映射"""
        return {
            "female_interrupted": 5,      # 女性被打断 - 最高紧急
            "aggressive_context": 5,      # 攻击性语境 - 最高紧急
            "male_dominance": 4,          # 男性主导 - 高紧急
            "male_consecutive": 4,        # 男性连续发言 - 高紧急
            "female_ignored": 3,          # 女性被忽视 - 中等紧急
            "expression_difficulty": 3,   # 表达困难 - 中等紧急
            "gender_imbalance": 2,        # 性别不平衡 - 低紧急
        }
    
    def convert_detector_trigger(self, detector_trigger: str) -> UnifiedTriggerType:
        """转换检测器触发类型为统一触发类型"""
        return self.trigger_mappings.get(detector_trigger, UnifiedTriggerType.GENDER_IMBALANCE)
    
    def get_strategy_for_trigger(self, unified_trigger: UnifiedTriggerType, urgency_level: int) -> UnifiedTKIStrategy:
        """根据统一触发类型和紧急程度获取策略"""
        if unified_trigger not in self.strategy_mappings:
            return UnifiedTKIStrategy.COLLABORATING
        
        # 确保紧急程度在1-5范围内
        urgency_level = max(1, min(5, urgency_level))
        
        return self.strategy_mappings[unified_trigger].get(urgency_level, UnifiedTKIStrategy.COLLABORATING)
    
    def get_urgency_for_trigger(self, trigger: str) -> int:
        """根据触发类型获取默认紧急程度"""
        return self.urgency_mappings.get(trigger, 1)
    
    def get_trigger_description(self, trigger: UnifiedTriggerType) -> str:
        """获取触发类型描述"""
        descriptions = {
            UnifiedTriggerType.FEMALE_INTERRUPTED: "女性说话被打断",
            UnifiedTriggerType.FEMALE_IGNORED: "女性说完话没人理她",
            UnifiedTriggerType.MALE_DOMINANCE: "男性主导对话",
            UnifiedTriggerType.MALE_CONSECUTIVE: "男性连续发言",
            UnifiedTriggerType.GENDER_IMBALANCE: "性别不平衡",
            UnifiedTriggerType.EXPRESSION_DIFFICULTY: "女性表达困难",
            UnifiedTriggerType.AGGRESSIVE_CONTEXT: "攻击性语境"
        }
        return descriptions.get(trigger, "未知触发类型")
    
    def get_strategy_description(self, strategy: UnifiedTKIStrategy) -> str:
        """获取策略描述"""
        descriptions = {
            UnifiedTKIStrategy.COLLABORATING: "协作型 - 整合各方观点，推动共识",
            UnifiedTKIStrategy.ACCOMMODATING: "迁就型 - 关系优先，安抚他人",
            UnifiedTKIStrategy.COMPETING: "竞争型 - 强势捍卫女性表达权",
            UnifiedTKIStrategy.COMPROMISING: "妥协型 - 设置公平讨论机制",
            UnifiedTKIStrategy.AVOIDING: "回避型 - 逃避冲突，转移话题",
            UnifiedTKIStrategy.AUTO: "自动选择 - 根据情况自动判断"
        }
        return descriptions.get(strategy, "未知策略")
    
    def validate_consistency(self) -> Dict[str, bool]:
        """验证detectors和interventions之间的一致性"""
        consistency_report = {
            "trigger_types_consistent": True,
            "strategy_mappings_consistent": True,
            "urgency_levels_consistent": True
        }
        
        # 检查触发类型一致性
        expected_triggers = {
            "female_interrupted", "female_ignored", "male_dominance",
            "male_consecutive", "gender_imbalance", "expression_difficulty", "aggressive_context"
        }
        
        actual_triggers = set(self.trigger_mappings.keys())
        consistency_report["trigger_types_consistent"] = expected_triggers.issubset(actual_triggers)
        
        # 检查策略映射完整性
        for trigger in UnifiedTriggerType:
            if trigger not in self.strategy_mappings:
                consistency_report["strategy_mappings_consistent"] = False
                break
        
        # 检查紧急程度映射完整性
        for trigger in expected_triggers:
            if trigger not in self.urgency_mappings:
                consistency_report["urgency_levels_consistent"] = False
                break
        
        return consistency_report 