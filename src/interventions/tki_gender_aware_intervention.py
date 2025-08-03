"""
基于TKI模型的性别意识干预策略生成器
专门针对性别结构性边缘化行为设计五种风格的干预策略
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class TKIStrategy(Enum):
    """TKI冲突管理策略"""
    COLLABORATING = "collaborating"    # 协作型：高自我关注 + 高他人关注
    ACCOMMODATING = "accommodating"    # 迁就型：低自我关注 + 高他人关注
    COMPETING = "competing"            # 竞争型：高自我关注 + 低他人关注
    COMPROMISING = "compromising"      # 妥协型：中等自我关注 + 中等他人关注
    AVOIDING = "avoiding"              # 回避型：低自我关注 + 低他人关注

class InterruptionType(Enum):
    """打断类型"""
    STRUCTURAL_MARGINALIZATION = "structural_marginalization"  # 结构性边缘化
    EXPRESSION_DIFFICULTY = "expression_difficulty"           # 表达困难
    POTENTIAL_AGGRESSION = "potential_aggression"            # 潜在攻击性

@dataclass
class TKIInterventionTemplate:
    """TKI干预模板"""
    strategy: TKIStrategy
    interruption_type: InterruptionType
    template: str
    tone: str
    self_concern: int  # 1-5级，对女性表达的支持程度
    other_concern: int  # 1-5级，对群体氛围的维护程度
    behavior_keywords: List[str]
    use_case: str

class TKIGenderAwareInterventionGenerator:
    """基于TKI模型的性别意识干预生成器"""
    
    def __init__(self):
        self.templates = self._initialize_tki_templates()
        self.strategy_weights = self._initialize_strategy_weights()
    
    def _initialize_tki_templates(self) -> Dict[TKIStrategy, List[TKIInterventionTemplate]]:
        """初始化TKI干预模板"""
        return {
            TKIStrategy.COLLABORATING: self._get_collaborating_templates(),
            TKIStrategy.ACCOMMODATING: self._get_accommodating_templates(),
            TKIStrategy.COMPETING: self._get_competing_templates(),
            TKIStrategy.COMPROMISING: self._get_compromising_templates(),
            TKIStrategy.AVOIDING: self._get_avoiding_templates()
        }
    
    def _get_collaborating_templates(self) -> List[TKIInterventionTemplate]:
        """协作型模板：双赢，整合立场，推动共识"""
        return [
            TKIInterventionTemplate(
                strategy=TKIStrategy.COLLABORATING,
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                template="她的观察也挺细的，{女性观点}。其实{男性观点}和{女性观点}也能互补，蛮值得讨论的。",
                tone="respectful_logical",
                self_concern=5,  # 高：正面支持观点、内容认同
                other_concern=5,  # 高：整合他人视角，重建和谐
                behavior_keywords=["协同", "共同探讨", "价值整合"],
                use_case="male_dominance"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.COLLABORATING,
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                template="{女性用户}提到的{观点}很有价值，让我们一起来完善这个想法？",
                tone="supportive_integrative",
                self_concern=5,
                other_concern=4,
                behavior_keywords=["观点整合", "共同完善", "价值认可"],
                use_case="expression_support"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.COLLABORATING,
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                template="每个观点都值得认真对待。{女性观点}和{男性观点}都有道理，让我们找到共同点？",
                tone="balanced_analytical",
                self_concern=4,
                other_concern=5,
                behavior_keywords=["观点整合", "寻找共识", "理性讨论"],
                use_case="aggression_mediation"
            )
        ]
    
    def _get_accommodating_templates(self) -> List[TKIInterventionTemplate]:
        """迁就型模板：关系优先，安抚他人，减少冲突"""
        return [
            TKIInterventionTemplate(
                strategy=TKIStrategy.ACCOMMODATING,
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                template="她就是挺喜欢{话题}的～每个人表达方式不一样嘛。",
                tone="soft_supportive",
                self_concern=3,  # 中：认可其表达权，但不坚持其内容
                other_concern=5,  # 高：回避冲突、缓解紧张
                behavior_keywords=["退让", "缓和语气", "表达理解"],
                use_case="female_ignored"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.ACCOMMODATING,
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                template="没关系，慢慢说，我们理解你想表达的意思。",
                tone="gentle_understanding",
                self_concern=3,
                other_concern=5,
                behavior_keywords=["理解", "支持", "耐心"],
                use_case="hesitation_support"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.ACCOMMODATING,
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                template="大家都有表达的权利，让我们保持友好的讨论氛围。",
                tone="harmonious",
                self_concern=3,
                other_concern=5,
                behavior_keywords=["和谐", "包容", "理解"],
                use_case="tension_reduction"
            )
        ]
    
    def _get_competing_templates(self) -> List[TKIInterventionTemplate]:
        """竞争型模板：立场鲜明，为女性据理力争"""
        return [
            TKIInterventionTemplate(
                strategy=TKIStrategy.COMPETING,
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                template="别因为她是女生就否定她的分析，她说得很专业，你听听再评价吧。",
                tone="assertive_direct",
                self_concern=5,  # 高：正面反击排斥行为
                other_concern=2,  # 低：可能引起对方反感或对立升级
                behavior_keywords=["指出不公", "立场鲜明", "对抗性语句"],
                use_case="female_interrupted"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.COMPETING,
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                template="她的观点很有价值，让我们认真听听她的想法。",
                tone="defensive_supportive",
                self_concern=5,
                other_concern=2,
                behavior_keywords=["捍卫", "支持", "强调价值"],
                use_case="expression_defense"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.COMPETING,
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                template="这种性别偏见是不对的，每个人都有平等的表达权利。",
                tone="confrontational",
                self_concern=5,
                other_concern=1,
                behavior_keywords=["对抗", "指出偏见", "强调公平"],
                use_case="bias_confrontation"
            )
        ]
    
    def _get_compromising_templates(self) -> List[TKIInterventionTemplate]:
        """妥协型模板：平衡，保障每方都能发声"""
        return [
            TKIInterventionTemplate(
                strategy=TKIStrategy.COMPROMISING,
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                template="要不我们轮流说说{话题}，再讲讲各自的看法？她还没说完呢。",
                tone="neutral_practical",
                self_concern=3,  # 中：提供发言机会，但不参与立场判断
                other_concern=3,  # 中：减少抢话、打断，通过结构控制缓和
                behavior_keywords=["轮流说话", "发言顺序", "共识中点"],
                use_case="turn_taking"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.COMPROMISING,
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                template="让我们给每个人平等的表达时间，{女性用户}你想说什么？",
                tone="fair_balanced",
                self_concern=3,
                other_concern=3,
                behavior_keywords=["平等", "公平", "机会均等"],
                use_case="equal_opportunity"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.COMPROMISING,
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                template="让我们设定一个讨论规则：每个人都能完整表达，不被打断。",
                tone="structural_neutral",
                self_concern=3,
                other_concern=3,
                behavior_keywords=["规则设定", "流程控制", "结构平衡"],
                use_case="rule_setting"
            )
        ]
    
    def _get_avoiding_templates(self) -> List[TKIInterventionTemplate]:
        """回避型模板：逃避冲突，绕开矛盾话题"""
        return [
            TKIInterventionTemplate(
                strategy=TKIStrategy.AVOIDING,
                interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
                template="哈哈别杠啦～今晚{话题}比赛几点开始来着？",
                tone="casual_deflective",
                self_concern=1,  # 低：不提供任何表达支持
                other_concern=2,  # 低：也不真正维持和谐，仅跳过问题
                behavior_keywords=["岔开话题", "模糊", "轻描淡写"],
                use_case="topic_shift"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.AVOIDING,
                interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
                template="这个确实比较复杂，要不我们先聊点别的？",
                tone="evasive_humorous",
                self_concern=1,
                other_concern=2,
                behavior_keywords=["回避", "转移", "轻松化"],
                use_case="difficulty_avoidance"
            ),
            TKIInterventionTemplate(
                strategy=TKIStrategy.AVOIDING,
                interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
                template="大家都有不同的看法，这很正常。我们聊点轻松的吧？",
                tone="dismissive_light",
                self_concern=1,
                other_concern=2,
                behavior_keywords=["淡化", "忽略", "转移注意力"],
                use_case="conflict_avoidance"
            )
        ]
    
    def _initialize_strategy_weights(self) -> Dict[TKIStrategy, Dict[str, float]]:
        """初始化策略权重"""
        return {
            TKIStrategy.COLLABORATING: {
                "self_concern_weight": 0.5,
                "other_concern_weight": 0.5,
                "preferred_scenarios": ["male_dominance", "expression_support"]
            },
            TKIStrategy.ACCOMMODATING: {
                "self_concern_weight": 0.3,
                "other_concern_weight": 0.7,
                "preferred_scenarios": ["tension_reduction", "hesitation_support"]
            },
            TKIStrategy.COMPETING: {
                "self_concern_weight": 0.8,
                "other_concern_weight": 0.2,
                "preferred_scenarios": ["female_interrupted", "bias_confrontation"]
            },
            TKIStrategy.COMPROMISING: {
                "self_concern_weight": 0.5,
                "other_concern_weight": 0.5,
                "preferred_scenarios": ["turn_taking", "equal_opportunity"]
            },
            TKIStrategy.AVOIDING: {
                "self_concern_weight": 0.2,
                "other_concern_weight": 0.3,
                "preferred_scenarios": ["topic_shift", "conflict_avoidance"]
            }
        }
    
    def select_strategy(self, interruption_type: InterruptionType, 
                       context: Dict, urgency_level: int) -> TKIStrategy:
        """根据情境选择TKI策略"""
        
        # 根据紧急程度调整策略选择
        if urgency_level >= 5:
            # 高紧急程度 - 倾向于竞争型或协作型
            return random.choice([TKIStrategy.COMPETING, TKIStrategy.COLLABORATING])
        elif urgency_level >= 4:
            # 中高紧急程度 - 倾向于协作型或迁就型
            return random.choice([TKIStrategy.COLLABORATING, TKIStrategy.ACCOMMODATING])
        elif urgency_level >= 3:
            # 中等紧急程度 - 倾向于妥协型
            return TKIStrategy.COMPROMISING
        else:
            # 低紧急程度 - 倾向于回避型或迁就型
            return random.choice([TKIStrategy.AVOIDING, TKIStrategy.ACCOMMODATING])
    
    def generate_intervention(self, strategy: TKIStrategy, 
                            interruption_type: InterruptionType,
                            context: Dict) -> str:
        """生成干预消息"""
        
        # 获取对应策略的模板
        templates = self.templates.get(strategy, [])
        suitable_templates = [t for t in templates if t.interruption_type == interruption_type]
        
        if not suitable_templates:
            # 如果没有匹配的模板，使用该策略的第一个模板
            suitable_templates = templates[:1] if templates else []
        
        if not suitable_templates:
            # 默认消息
            return "🤝 让我们继续建设性的讨论。"
        
        # 选择模板
        template = random.choice(suitable_templates)
        
        # 填充模板变量
        message = self._fill_template(template.template, context)
        
        return message
    
    def _fill_template(self, template: str, context: Dict) -> str:
        """填充模板变量"""
        
        # 替换用户占位符
        if "女性用户" in template and context.get("female_participants"):
            template = template.replace("女性用户", context["female_participants"][0])
        
        if "男性用户" in template and context.get("male_participants"):
            template = template.replace("男性用户", context["male_participants"][0])
        
        # 替换观点占位符
        if "女性观点" in template:
            template = template.replace("女性观点", context.get("female_viewpoint", "这个观点"))
        
        if "男性观点" in template:
            template = template.replace("男性观点", context.get("male_viewpoint", "那个观点"))
        
        # 替换话题占位符
        if "话题" in template:
            template = template.replace("话题", context.get("current_topic", "这个话题"))
        
        return template
    
    def get_strategy_analysis(self, strategy: TKIStrategy) -> Dict:
        """获取策略分析"""
        weights = self.strategy_weights.get(strategy, {})
        templates = self.templates.get(strategy, [])
        
        return {
            "strategy": strategy.value,
            "self_concern_weight": weights.get("self_concern_weight", 0.5),
            "other_concern_weight": weights.get("other_concern_weight", 0.5),
            "preferred_scenarios": weights.get("preferred_scenarios", []),
            "template_count": len(templates),
            "interruption_types": list(set(t.interruption_type.value for t in templates))
        }
    
    def get_prompt_template(self, strategy: TKIStrategy) -> str:
        """获取策略的Prompt模板"""
        
        prompt_templates = {
            TKIStrategy.COLLABORATING: """You are a chatbot acting as a neutral moderator in a three-person group chat about table tennis. Your task is to insert short, context-aware comments at appropriate moments to mediate conversational imbalance. Do not dominate the conversation. Only respond with 1–2 short sentences per intervention.

Your conflict style is Collaborating. You aim to integrate everyone's viewpoints and encourage mutual understanding. Use a respectful, logical tone. Try to bridge disagreements and highlight shared interests or valid points from both sides. Invite elaboration or synthesis.""",
            
            TKIStrategy.ACCOMMODATING: """You are a chatbot acting as a neutral moderator in a three-person group chat about table tennis. Your task is to insert short, context-aware comments at appropriate moments to mediate conversational imbalance. Do not dominate the conversation. Only respond with 1–2 short sentences per intervention.

Your conflict style is Accommodating. You prioritize maintaining harmony in the group, even if it means giving up your own stance. Use soft, supportive language. Avoid taking sides, and gently affirm the marginalized person's right to speak without challenging others.""",
            
            TKIStrategy.COMPETING: """You are a chatbot acting as a neutral moderator in a three-person group chat about table tennis. Your task is to insert short, context-aware comments at appropriate moments to mediate conversational imbalance. Do not dominate the conversation. Only respond with 1–2 short sentences per intervention.

Your conflict style is Competing. You strongly defend the marginalized speaker's right to speak, even if it causes confrontation. Use assertive, direct language. Call out biased or exclusionary behavior without hesitation. You prioritize fairness over politeness.""",
            
            TKIStrategy.COMPROMISING: """You are a chatbot acting as a neutral moderator in a three-person group chat about table tennis. Your task is to insert short, context-aware comments at appropriate moments to mediate conversational imbalance. Do not dominate the conversation. Only respond with 1–2 short sentences per intervention.

Your conflict style is Compromising. Your goal is to quickly balance the conversation so everyone gets a fair chance to speak. Use neutral, practical language. Suggest taking turns or splitting time to reduce tension and ensure equal participation.""",
            
            TKIStrategy.AVOIDING: """You are a chatbot acting as a neutral moderator in a three-person group chat about table tennis. Your task is to insert short, context-aware comments at appropriate moments to mediate conversational imbalance. Do not dominate the conversation. Only respond with 1–2 short sentences per intervention.

Your conflict style is Avoiding. You try to reduce tension by shifting attention away from conflict. You don't take sides and avoid directly addressing disagreements. Use casual, deflective, or humorous language to steer the group toward a lighter topic."""
        }
        
        return prompt_templates.get(strategy, prompt_templates[TKIStrategy.COLLABORATING])
    
    def get_strategy_comparison(self) -> Dict:
        """获取策略对比表"""
        comparison = {
            "strategies": [],
            "summary": {
                "total_strategies": len(TKIStrategy),
                "total_templates": sum(len(templates) for templates in self.templates.values())
            }
        }
        
        for strategy in TKIStrategy:
            analysis = self.get_strategy_analysis(strategy)
            comparison["strategies"].append({
                "name": strategy.value,
                "self_concern": analysis["self_concern_weight"],
                "other_concern": analysis["other_concern_weight"],
                "template_count": analysis["template_count"],
                "preferred_scenarios": analysis["preferred_scenarios"]
            })
        
        return comparison