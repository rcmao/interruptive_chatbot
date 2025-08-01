"""
Appendix A. Prompt Template Library for Conflict Intervention

This module provides a categorized library of prompt templates used by the chatbot, 
designed according to the five conflict management styles proposed by the 
Thomas-Kilmann Instrument (TKI). These prompts are used to steer conversations 
during conflict episodes in multi-party chat environments.

Author: Interruptive Chatbot System
Version: 1.0
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class TKIStrategy(Enum):
    """Thomas-Kilmann Conflict Mode Instrument Strategies"""
    COLLABORATING = "collaborating"    # High concern for self & others
    ACCOMMODATING = "accommodating"    # Low concern for self, high for others
    COMPETING = "competing"            # High concern for self, low for others
    AVOIDING = "avoiding"              # Low concern for self & others
    COMPROMISING = "compromising"      # Moderate concern for both

@dataclass
class PromptTemplate:
    """Prompt template data structure"""
    id: str
    content: str
    context: str
    emotion_tone: str
    use_case: str

class PromptTemplateLibrary:
    """Comprehensive prompt template library for conflict intervention"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[TKIStrategy, List[PromptTemplate]]:
        """Initialize all prompt templates"""
        return {
            TKIStrategy.COLLABORATING: self._get_collaborating_templates(),
            TKIStrategy.ACCOMMODATING: self._get_accommodating_templates(),
            TKIStrategy.COMPETING: self._get_competing_templates(),
            TKIStrategy.AVOIDING: self._get_avoiding_templates(),
            TKIStrategy.COMPROMISING: self._get_compromising_templates()
        }
    
    def _get_collaborating_templates(self) -> List[PromptTemplate]:
        """A.1 Collaborating Style (High Concern for Self & Others)"""
        return [
            PromptTemplate(
                id="C1",
                content="I see we're both aiming for a good outcome—how about we combine our ideas?",
                context="When both parties have valid but different approaches",
                emotion_tone="cooperative",
                use_case="early_conflict_phase"
            ),
            PromptTemplate(
                id="C2",
                content="Let's figure this out together. What do you think is a fair way forward?",
                context="Seeking mutual understanding and agreement",
                emotion_tone="inclusive",
                use_case="divergence_phase"
            ),
            PromptTemplate(
                id="C3",
                content="We both care about this. Can we schedule a quick sync to align?",
                context="When immediate resolution isn't possible",
                emotion_tone="patient",
                use_case="complex_conflict"
            ),
            PromptTemplate(
                id="C4",
                content="It seems like we're looking at different aspects—can we clarify and co-create a solution?",
                context="Different perspectives on the same issue",
                emotion_tone="analytical",
                use_case="misunderstanding"
            ),
            PromptTemplate(
                id="C5",
                content="Both points are valid—how can we integrate them?",
                context="Multiple valid approaches exist",
                emotion_tone="integrative",
                use_case="solution_integration"
            ),
            PromptTemplate(
                id="C6",
                content="What's the most important priority for you here?",
                context="Understanding underlying needs",
                emotion_tone="curious",
                use_case="needs_clarification"
            ),
            PromptTemplate(
                id="C7",
                content="Let's find common ground that works for both sides.",
                context="Seeking win-win solutions",
                emotion_tone="optimistic",
                use_case="resolution_seeking"
            ),
            PromptTemplate(
                id="C8",
                content="Can we revisit the goal and see how both suggestions might support it?",
                context="Refocusing on shared objectives",
                emotion_tone="reflective",
                use_case="goal_alignment"
            ),
            PromptTemplate(
                id="C9",
                content="This seems like a shared challenge—want to brainstorm together?",
                context="Complex problem requiring collaboration",
                emotion_tone="encouraging",
                use_case="complex_problem"
            ),
            PromptTemplate(
                id="C10",
                content="I believe a win-win is possible. Shall we try?",
                context="Encouraging collaborative effort",
                emotion_tone="hopeful",
                use_case="motivation"
            )
        ]
    
    def _get_accommodating_templates(self) -> List[PromptTemplate]:
        """A.2 Accommodating Style (Low Concern for Self, High Concern for Others)"""
        return [
            PromptTemplate(
                id="A1",
                content="I can adjust my part—what works best for you?",
                context="Willing to adapt for others",
                emotion_tone="flexible",
                use_case="relationship_preservation"
            ),
            PromptTemplate(
                id="A2",
                content="I understand your concerns. I'll go with your suggestion.",
                context="Acknowledging others' needs",
                emotion_tone="supportive",
                use_case="deferral"
            ),
            PromptTemplate(
                id="A3",
                content="No worries, I can step back here.",
                context="Voluntary withdrawal",
                emotion_tone="gracious",
                use_case="tension_reduction"
            ),
            PromptTemplate(
                id="A4",
                content="Happy to support your direction if that helps the team.",
                context="Team-oriented accommodation",
                emotion_tone="team_focused",
                use_case="team_harmony"
            ),
            PromptTemplate(
                id="A5",
                content="You've got a strong point—let's go with that.",
                context="Acknowledging strong arguments",
                emotion_tone="respectful",
                use_case="strong_argument"
            ),
            PromptTemplate(
                id="A6",
                content="I'm flexible on this. Let me know what you prefer.",
                context="Showing flexibility",
                emotion_tone="open",
                use_case="preference_deferral"
            ),
            PromptTemplate(
                id="A7",
                content="That makes sense—I'm okay deferring to you.",
                context="Logical deference",
                emotion_tone="reasonable",
                use_case="logical_choice"
            ),
            PromptTemplate(
                id="A8",
                content="I'll follow your lead this time.",
                context="Temporary leadership transfer",
                emotion_tone="trusting",
                use_case="leadership_rotation"
            ),
            PromptTemplate(
                id="A9",
                content="You seem passionate about this—go ahead, I'll adapt.",
                context="Recognizing passion and commitment",
                emotion_tone="appreciative",
                use_case="passion_recognition"
            ),
            PromptTemplate(
                id="A10",
                content="I'll adjust to make things smoother for you.",
                context="Smoothing the process",
                emotion_tone="helpful",
                use_case="process_smoothing"
            )
        ]
    
    def _get_competing_templates(self) -> List[PromptTemplate]:
        """A.3 Competing Style (High Concern for Self, Low Concern for Others)"""
        return [
            PromptTemplate(
                id="CP1",
                content="I strongly believe this is the best approach—we should move forward with it.",
                context="Firm conviction in approach",
                emotion_tone="assertive",
                use_case="urgent_decision"
            ),
            PromptTemplate(
                id="CP2",
                content="Let's make a firm decision. I suggest we proceed with my proposal.",
                context="Need for decisive action",
                emotion_tone="decisive",
                use_case="deadlock_breaking"
            ),
            PromptTemplate(
                id="CP3",
                content="Time is limited—we need to pick the most effective solution now.",
                context="Time pressure situation",
                emotion_tone="urgent",
                use_case="time_constraint"
            ),
            PromptTemplate(
                id="CP4",
                content="I've evaluated the options and this path is the most strategic.",
                context="Strategic analysis completed",
                emotion_tone="analytical",
                use_case="strategic_choice"
            ),
            PromptTemplate(
                id="CP5",
                content="Let's prioritize results—this method gets us there faster.",
                context="Results-focused approach",
                emotion_tone="results_oriented",
                use_case="efficiency_focus"
            ),
            PromptTemplate(
                id="CP6",
                content="I understand the risks, and I'm willing to take responsibility.",
                context="Risk acceptance with accountability",
                emotion_tone="responsible",
                use_case="risk_management"
            ),
            PromptTemplate(
                id="CP7",
                content="This is non-negotiable for me—it aligns with our critical goals.",
                context="Critical goal alignment",
                emotion_tone="firm",
                use_case="critical_goals"
            ),
            PromptTemplate(
                id="CP8",
                content="Let's move ahead with the stronger plan.",
                context="Quality-based decision",
                emotion_tone="confident",
                use_case="quality_selection"
            ),
            PromptTemplate(
                id="CP9",
                content="I appreciate other views, but I stand by this direction.",
                context="Acknowledging alternatives while maintaining position",
                emotion_tone="respectful_but_firm",
                use_case="position_maintenance"
            ),
            PromptTemplate(
                id="CP10",
                content="For clarity and momentum, let's go with the option I proposed.",
                context="Clarity and momentum focus",
                emotion_tone="directive",
                use_case="momentum_building"
            )
        ]
    
    def _get_avoiding_templates(self) -> List[PromptTemplate]:
        """A.4 Avoiding Style (Low Concern for Self & Others)"""
        return [
            PromptTemplate(
                id="AV1",
                content="Maybe we should take a pause and revisit this later?",
                context="Temporary withdrawal for reflection",
                emotion_tone="suggestive",
                use_case="emotional_escalation"
            ),
            PromptTemplate(
                id="AV2",
                content="Let's give this some space and come back fresh.",
                context="Creating space for cooling down",
                emotion_tone="calming",
                use_case="high_tension"
            ),
            PromptTemplate(
                id="AV3",
                content="I'll step back for now to avoid further tension.",
                context="Voluntary withdrawal to reduce tension",
                emotion_tone="peaceful",
                use_case="tension_reduction"
            ),
            PromptTemplate(
                id="AV4",
                content="Maybe we can refocus on this in our next session?",
                context="Postponing to dedicated time",
                emotion_tone="organizational",
                use_case="time_management"
            ),
            PromptTemplate(
                id="AV5",
                content="I'm sensing tension—how about we park this for now?",
                context="Recognizing and addressing tension",
                emotion_tone="observant",
                use_case="tension_detection"
            ),
            PromptTemplate(
                id="AV6",
                content="This might not be the best time to resolve it—let's hold off.",
                context="Timing consideration",
                emotion_tone="practical",
                use_case="poor_timing"
            ),
            PromptTemplate(
                id="AV7",
                content="Perhaps we can skip this for now and return with more clarity.",
                context="Clarity-seeking postponement",
                emotion_tone="thoughtful",
                use_case="clarity_needed"
            ),
            PromptTemplate(
                id="AV8",
                content="Let's take some time to think and revisit this tomorrow.",
                context="Reflection period needed",
                emotion_tone="patient",
                use_case="reflection_needed"
            ),
            PromptTemplate(
                id="AV9",
                content="I'm okay waiting a bit to address this constructively.",
                context="Constructive delay",
                emotion_tone="constructive",
                use_case="constructive_timing"
            ),
            PromptTemplate(
                id="AV10",
                content="Let's not push this now—there may be a better moment soon.",
                context="Better timing anticipation",
                emotion_tone="optimistic",
                use_case="timing_optimization"
            )
        ]
    
    def _get_compromising_templates(self) -> List[PromptTemplate]:
        """A.5 Compromising Style (Moderate Concern for Both)"""
        return [
            PromptTemplate(
                id="CM1",
                content="How about we meet halfway on this?",
                context="Seeking middle ground",
                emotion_tone="balanced",
                use_case="middle_ground"
            ),
            PromptTemplate(
                id="CM2",
                content="Can we each adjust slightly to make this work?",
                context="Mutual adjustment needed",
                emotion_tone="flexible",
                use_case="mutual_adjustment"
            ),
            PromptTemplate(
                id="CM3",
                content="Maybe we can take part of both ideas and blend them?",
                context="Idea integration",
                emotion_tone="integrative",
                use_case="idea_blending"
            ),
            PromptTemplate(
                id="CM4",
                content="If I give on this part, would you consider my concern too?",
                context="Reciprocal concession",
                emotion_tone="reciprocal",
                use_case="reciprocal_compromise"
            ),
            PromptTemplate(
                id="CM5",
                content="Let's find a balanced way forward.",
                context="Balanced solution seeking",
                emotion_tone="balanced",
                use_case="balanced_solution"
            ),
            PromptTemplate(
                id="CM6",
                content="What's one thing you can flex on, and I'll do the same?",
                context="Equal flexibility request",
                emotion_tone="fair",
                use_case="equal_flexibility"
            ),
            PromptTemplate(
                id="CM7",
                content="I'm open to concessions if it helps us agree.",
                context="Willingness to concede",
                emotion_tone="open",
                use_case="agreement_seeking"
            ),
            PromptTemplate(
                id="CM8",
                content="Would a hybrid solution work here?",
                context="Hybrid approach suggestion",
                emotion_tone="innovative",
                use_case="hybrid_solution"
            ),
            PromptTemplate(
                id="CM9",
                content="Let's both make a small tradeoff to keep progress moving.",
                context="Progress-focused compromise",
                emotion_tone="progress_oriented",
                use_case="progress_maintenance"
            ),
            PromptTemplate(
                id="CM10",
                content="I suggest we each pick one priority and meet in the middle.",
                context="Priority-based compromise",
                emotion_tone="strategic",
                use_case="priority_compromise"
            )
        ]
    
    def get_templates_for_strategy(self, strategy: TKIStrategy) -> List[PromptTemplate]:
        """Get all templates for a specific strategy"""
        return self.templates.get(strategy, [])
    
    def get_random_template(self, strategy: TKIStrategy) -> Optional[PromptTemplate]:
        """Get a random template for a specific strategy"""
        import random
        templates = self.get_templates_for_strategy(strategy)
        return random.choice(templates) if templates else None
    
    def get_template_by_id(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a specific template by ID"""
        for strategy_templates in self.templates.values():
            for template in strategy_templates:
                if template.id == template_id:
                    return template
        return None
    
    def get_templates_by_context(self, context: str) -> List[PromptTemplate]:
        """Get templates that match a specific context"""
        matching_templates = []
        for strategy_templates in self.templates.values():
            for template in strategy_templates:
                if context.lower() in template.context.lower():
                    matching_templates.append(template)
        return matching_templates
    
    def get_templates_by_emotion_tone(self, emotion_tone: str) -> List[PromptTemplate]:
        """Get templates that match a specific emotion tone"""
        matching_templates = []
        for strategy_templates in self.templates.values():
            for template in strategy_templates:
                if emotion_tone.lower() in template.emotion_tone.lower():
                    matching_templates.append(template)
        return matching_templates

# 创建全局模板库实例
prompt_library = PromptTemplateLibrary()

def get_prompt_template(strategy: TKIStrategy, context: str = None) -> str:
    """
    获取指定策略的提示模板
    
    Args:
        strategy: TKI策略类型
        context: 可选的上下文信息
    
    Returns:
        格式化的提示模板字符串
    """
    template = prompt_library.get_random_template(strategy)
    if template:
        return template.content
    return "Let's work together to resolve this."

def format_template_with_context(template: PromptTemplate, **kwargs) -> str:
    """
    使用上下文信息格式化模板
    
    Args:
        template: 提示模板对象
        kwargs: 要填充的上下文变量
    
    Returns:
        格式化后的提示字符串
    """
    content = template.content
    
    # 替换常见的上下文变量
    replacements = {
        "{user_a}": kwargs.get("user_a", "一位成员"),
        "{user_b}": kwargs.get("user_b", "另一位成员"),
        "{topic}": kwargs.get("topic", "当前讨论"),
        "{issue}": kwargs.get("issue", "这个问题"),
        "{goal}": kwargs.get("goal", "我们的目标"),
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    return content

# 使用示例
if __name__ == "__main__":
    # 测试模板库功能
    print("🧪 测试Prompt Template Library")
    print("=" * 50)
    
    # 获取协作策略的模板
    collaborating_templates = prompt_library.get_templates_for_strategy(TKIStrategy.COLLABORATING)
    print(f"协作策略模板数量: {len(collaborating_templates)}")
    
    # 获取随机模板
    random_template = prompt_library.get_random_template(TKIStrategy.COMPROMISING)
    if random_template:
        print(f"随机妥协模板: {random_template.content}")
    
    # 按上下文查找模板
    tension_templates = prompt_library.get_templates_by_context("tension")
    print(f"与紧张相关的模板数量: {len(tension_templates)}")
    
    # 格式化模板
    formatted = format_template_with_context(
        random_template,
        user_a="张三",
        user_b="李四",
        topic="项目方案"
    )
    print(f"格式化后的模板: {formatted}") 