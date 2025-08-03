"""
增强的干预生成器 - 支持admin选择的风格
根据检测结果和admin设置的风格生成合适的干预内容
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class AdminInterventionStyle(Enum):
    """Admin可选择的干预风格"""
    COLLABORATING = "collaborating"    # 协作型
    ACCOMMODATING = "accommodating"    # 迁就型
    COMPETING = "competing"            # 竞争型
    COMPROMISING = "compromising"      # 妥协型
    AVOIDING = "avoiding"              # 回避型
    AUTO = "auto"                      # 自动选择

class EnhancedInterventionTrigger(Enum):
    """增强的干预触发类型"""
    FEMALE_INTERRUPTED = "female_interrupted"      # 女性被打断
    FEMALE_IGNORED = "female_ignored"              # 女性被忽视
    MALE_DOMINANCE = "male_dominance"              # 男性主导对话
    MALE_CONSECUTIVE = "male_consecutive"          # 男性连续发言
    GENDER_IMBALANCE = "gender_imbalance"          # 性别不平衡
    EXPRESSION_DIFFICULTY = "expression_difficulty"  # 表达困难
    AGGRESSIVE_CONTEXT = "aggressive_context"      # 攻击性语境

@dataclass
class InterventionContext:
    """干预上下文"""
    trigger_type: EnhancedInterventionTrigger
    urgency_level: int
    confidence: float
    recent_messages: List[Dict]
    female_participants: List[str]
    male_participants: List[str]
    current_topic: Optional[str] = None
    admin_style: AdminInterventionStyle = AdminInterventionStyle.AUTO

class EnhancedInterventionGenerator:
    """增强的干预生成器"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.style_mappings = self._initialize_style_mappings()
    
    def _initialize_templates(self) -> Dict[AdminInterventionStyle, Dict[str, List[str]]]:
        """初始化干预模板"""
        return {
            AdminInterventionStyle.COLLABORATING: {
                "female_interrupted": [
                    "让我们给{女性用户}一个完整表达的机会，她的观点很有价值。",
                    "我注意到{女性用户}刚才想说什么，让我们听听她的想法？",
                    "每个观点都值得认真对待，{女性用户}请继续。"
                ],
                "aggressive_context": [
                    "让我们保持建设性的讨论氛围，每个人都有表达的权利。",
                    "每个观点都有其价值，让我们找到共同点？",
                    "我理解大家的热情，但让我们用更包容的方式交流。"
                ],
                "male_consecutive": [
                    "讨论很热烈！{女性用户}，你对这个话题有什么想法吗？",
                    "让我们听听不同的观点，{女性用户}你觉得呢？",
                    "这个话题很有趣，{女性用户}你有什么看法？"
                ],
                "expression_difficulty": [
                    "慢慢说，我们在听。{女性用户}你想表达的是...？",
                    "你的观点很重要，让我们一起来完善这个想法？",
                    "没关系，慢慢表达，我们理解你想说的。"
                ]
            },
            AdminInterventionStyle.ACCOMMODATING: {
                "female_interrupted": [
                    "她就是挺喜欢这个话题的～每个人表达方式不一样嘛。",
                    "没关系，慢慢说，我们理解你想表达的意思。",
                    "你的观点很有价值，让我们一起来完善这个想法？"
                ],
                "aggressive_context": [
                    "大家都有表达的权利，让我们保持友好的讨论氛围。",
                    "每个人都有自己的看法，这很正常。",
                    "让我们用更温和的方式交流。"
                ],
                "male_consecutive": [
                    "这个话题确实很有趣，{女性用户}你有什么想法吗？",
                    "我们都很关心这个话题，{女性用户}你觉得呢？",
                    "让我们听听{女性用户}的看法。"
                ],
                "expression_difficulty": [
                    "没关系，慢慢说，我们理解你想表达的意思。",
                    "你的观点很有价值，让我们一起来完善这个想法？",
                    "慢慢表达，我们都在听。"
                ]
            },
            AdminInterventionStyle.COMPETING: {
                "female_interrupted": [
                    "别因为她是女生就否定她的分析，她说得很专业，你听听再评价吧。",
                    "让她说完，每个人都有平等的表达权利。",
                    "这种打断是不公平的，{女性用户}请继续。"
                ],
                "aggressive_context": [
                    "这种性别偏见是不对的，每个人都有平等的表达权利。",
                    "攻击性言论是不可接受的，让我们保持尊重。",
                    "每个人都有表达的权利，不应该被歧视。"
                ],
                "male_consecutive": [
                    "让我们给{女性用户}一个表达的机会，她的观点同样重要。",
                    "不能只有男性在发言，{女性用户}请说说你的看法。",
                    "每个人都有发言权，{女性用户}请继续。"
                ],
                "expression_difficulty": [
                    "她的观点很有价值，让我们认真听听她的想法。",
                    "不要因为表达方式而忽视观点本身的价值。",
                    "每个观点都值得被认真对待。"
                ]
            },
            AdminInterventionStyle.COMPROMISING: {
                "female_interrupted": [
                    "要不我们轮流说说这个话题，再讲讲各自的看法？她还没说完呢。",
                    "让我们给每个人平等的表达时间，{女性用户}你想说什么？",
                    "我们设定一个规则：每个人都能完整表达，不被打断。"
                ],
                "aggressive_context": [
                    "让我们设定一个讨论规则：每个人都能完整表达，不被打断。",
                    "我们轮流发言，每个人都有机会表达。",
                    "让我们用更公平的方式讨论。"
                ],
                "male_consecutive": [
                    "让我们轮流发言，{女性用户}请说说你的看法。",
                    "每个人都有发言权，让我们给{女性用户}一个机会。",
                    "我们设定一个规则：轮流发言。"
                ],
                "expression_difficulty": [
                    "让我们给每个人平等的表达时间，{女性用户}你想说什么？",
                    "每个人都有表达的权利，让我们耐心倾听。",
                    "我们设定一个规则：给每个人充分的表达时间。"
                ]
            },
            AdminInterventionStyle.AVOIDING: {
                "female_interrupted": [
                    "哈哈别杠啦～今晚这个话题比赛几点开始来着？",
                    "这个确实比较复杂，要不我们先聊点别的？",
                    "大家都有不同的看法，这很正常。我们聊点轻松的吧？"
                ],
                "aggressive_context": [
                    "哈哈别杠啦～今晚这个话题比赛几点开始来着？",
                    "这个确实比较复杂，要不我们先聊点别的？",
                    "大家都有不同的看法，这很正常。我们聊点轻松的吧？"
                ],
                "male_consecutive": [
                    "哈哈别杠啦～今晚这个话题比赛几点开始来着？",
                    "这个确实比较复杂，要不我们先聊点别的？",
                    "大家都有不同的看法，这很正常。我们聊点轻松的吧？"
                ],
                "expression_difficulty": [
                    "哈哈别杠啦～今晚这个话题比赛几点开始来着？",
                    "这个确实比较复杂，要不我们先聊点别的？",
                    "大家都有不同的看法，这很正常。我们聊点轻松的吧？"
                ]
            }
        }
    
    def _initialize_style_mappings(self) -> Dict[EnhancedInterventionTrigger, AdminInterventionStyle]:
        """初始化触发类型到风格的映射"""
        return {
            EnhancedInterventionTrigger.FEMALE_INTERRUPTED: AdminInterventionStyle.COMPETING,
            EnhancedInterventionTrigger.AGGRESSIVE_CONTEXT: AdminInterventionStyle.COMPETING,
            EnhancedInterventionTrigger.MALE_DOMINANCE: AdminInterventionStyle.COLLABORATING,
            EnhancedInterventionTrigger.MALE_CONSECUTIVE: AdminInterventionStyle.COLLABORATING,
            EnhancedInterventionTrigger.EXPRESSION_DIFFICULTY: AdminInterventionStyle.ACCOMMODATING,
            EnhancedInterventionTrigger.FEMALE_IGNORED: AdminInterventionStyle.COMPROMISING,
            EnhancedInterventionTrigger.GENDER_IMBALANCE: AdminInterventionStyle.COMPROMISING
        }
    
    def generate_intervention(self, context: InterventionContext) -> str:
        """生成干预消息"""
        
        # 确定使用的风格
        style = self._determine_style(context)
        
        # 获取对应的模板
        trigger_key = context.trigger_type.value
        templates = self.templates.get(style, {}).get(trigger_key, [])
        
        if not templates:
            # 如果没有对应模板，使用默认消息
            return self._get_default_message(context)
        
        # 选择模板
        template = random.choice(templates)
        
        # 填充模板
        message = self._fill_template(template, context)
        
        return message
    
    def _determine_style(self, context: InterventionContext) -> AdminInterventionStyle:
        """确定使用的风格"""
        
        # 如果admin设置了特定风格且不是auto，使用admin设置的风格
        if context.admin_style != AdminInterventionStyle.AUTO:
            return context.admin_style
        
        # 否则根据触发类型和紧急程度自动选择
        base_style = self.style_mappings.get(context.trigger_type, AdminInterventionStyle.COLLABORATING)
        
        # 根据紧急程度调整风格
        if context.urgency_level >= 5:
            # 高紧急程度 - 倾向于竞争型
            return AdminInterventionStyle.COMPETING
        elif context.urgency_level >= 4:
            # 中高紧急程度 - 根据触发类型选择
            if context.trigger_type in [EnhancedInterventionTrigger.FEMALE_INTERRUPTED, EnhancedInterventionTrigger.AGGRESSIVE_CONTEXT]:
                return AdminInterventionStyle.COMPETING
            else:
                return AdminInterventionStyle.COLLABORATING
        elif context.urgency_level >= 3:
            # 中等紧急程度 - 倾向于妥协型
            return AdminInterventionStyle.COMPROMISING
        else:
            # 低紧急程度 - 倾向于回避型
            return AdminInterventionStyle.AVOIDING
    
    def _fill_template(self, template: str, context: InterventionContext) -> str:
        """填充模板变量"""
        
        # 替换用户占位符
        if "{女性用户}" in template and context.female_participants:
            template = template.replace("{女性用户}", context.female_participants[0])
        
        if "{男性用户}" in template and context.male_participants:
            template = template.replace("{男性用户}", context.male_participants[0])
        
        # 替换话题占位符
        if "这个话题" in template:
            template = template.replace("这个话题", context.current_topic or "这个话题")
        
        return template
    
    def _get_default_message(self, context: InterventionContext) -> str:
        """获取默认消息"""
        default_messages = {
            AdminInterventionStyle.COLLABORATING: "让我们继续建设性的讨论。",
            AdminInterventionStyle.ACCOMMODATING: "让我们保持友好的讨论氛围。",
            AdminInterventionStyle.COMPETING: "每个人都有平等的表达权利。",
            AdminInterventionStyle.COMPROMISING: "让我们给每个人平等的表达机会。",
            AdminInterventionStyle.AVOIDING: "我们聊点轻松的吧？"
        }
        
        style = self._determine_style(context)
        return default_messages.get(style, "让我们继续建设性的讨论。")
    
    def get_style_info(self, style: AdminInterventionStyle) -> Dict:
        """获取风格信息"""
        style_descriptions = {
            AdminInterventionStyle.COLLABORATING: {
                "name": "协作型",
                "description": "促进合作，整合不同观点，推动共识",
                "tone": "尊重、逻辑、整合",
                "best_for": ["男性主导", "性别不平衡", "需要平衡参与"]
            },
            AdminInterventionStyle.ACCOMMODATING: {
                "name": "迁就型", 
                "description": "关系优先，安抚他人，减少冲突",
                "tone": "温和、支持、理解",
                "best_for": ["表达困难", "紧张氛围", "需要缓和"]
            },
            AdminInterventionStyle.COMPETING: {
                "name": "竞争型",
                "description": "立场鲜明，为女性据理力争",
                "tone": "直接、坚定、保护",
                "best_for": ["女性被打断", "攻击性语境", "需要直接干预"]
            },
            AdminInterventionStyle.COMPROMISING: {
                "name": "妥协型",
                "description": "平衡，保障每方都能发声",
                "tone": "公平、平衡、规则",
                "best_for": ["女性被忽视", "需要轮流发言", "建立规则"]
            },
            AdminInterventionStyle.AVOIDING: {
                "name": "回避型",
                "description": "逃避冲突，绕开矛盾话题",
                "tone": "轻松、转移、淡化",
                "best_for": ["极端冲突", "需要转移话题", "暂时回避"]
            },
            AdminInterventionStyle.AUTO: {
                "name": "自动选择",
                "description": "根据触发类型和紧急程度自动选择最佳风格",
                "tone": "智能、自适应",
                "best_for": ["所有情况", "让系统自动判断"]
            }
        }
        
        return style_descriptions.get(style, {})
    
    def get_all_styles_info(self) -> Dict:
        """获取所有风格信息"""
        return {
            style.value: self.get_style_info(style)
            for style in AdminInterventionStyle
        } 