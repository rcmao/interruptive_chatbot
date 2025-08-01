"""
提示模板系统
"""

from enum import Enum
from typing import Dict, List, Optional
import random

class TKIStrategy(Enum):
    """TKI冲突管理策略"""
    COLLABORATING = "collaborating"
    ACCOMMODATING = "accommodating"
    COMPETING = "competing"
    AVOIDING = "avoiding"
    COMPROMISING = "compromising"

class PromptTemplateLibrary:
    """提示模板库"""
    
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self) -> Dict[str, List[str]]:
        """加载模板"""
        return {
            "collaborating": [
                "我理解大家都有压力，让我们先确认一下各自的情况？",
                "看起来大家对任务完成有不同的想法，我们能否一起讨论解决方案？",
                "我注意到有些分歧，让我们尝试找到共同点？"
            ],
            "accommodating": [
                "我理解你的处境，让我们先听听你的想法？",
                "也许我们可以先了解一下各自的困难？",
                "我理解你的担忧，让我们先暂停一下？"
            ],
            "competing": [
                "我们需要尽快解决这个问题，让我们直接面对它？",
                "时间紧迫，我们需要做出决定？",
                "让我们优先考虑结果，选择最有效的方案？"
            ],
            "avoiding": [
                "现在可能不是最好的讨论时机，我们能否先暂停一下？",
                "我感觉到大家的情绪都很激动，让我们先冷静一下？",
                "也许我们可以稍后再讨论这个问题？"
            ],
            "compromising": [
                "也许我们可以找到一个中间方案？",
                "双方都有道理，我们能否各让一步？",
                "让我们先达成一个临时协议，之后再完善？"
            ]
        }
    
    def get_template(self, strategy: str) -> str:
        """获取模板"""
        if strategy in self.templates:
            return random.choice(self.templates[strategy])
        return "让我们尝试找到解决方案。"
    
    def get_templates_for_strategy(self, strategy: str) -> List[str]:
        """获取指定策略的所有模板"""
        return self.templates.get(strategy, [])
