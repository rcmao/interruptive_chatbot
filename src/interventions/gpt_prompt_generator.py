"""
GPT提示生成器 - 按照工作流设计构造GPT prompt
负责将检测结果转换为GPT可理解的提示，生成符合TKI风格的插话内容
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class TriggerType(Enum):
    """插话触发类型 - 对应Discord实验场景"""
    FEMALE_INTERRUPTED = "❸"  # 女性说话被打断
    FEMALE_IGNORED = "❷"      # 女性说完话没人理她
    MALE_DOMINANCE = "❶"      # 男性主导对话
    EXPRESSION_DIFFICULTY = "❹"  # 女性表达困难
    AGGRESSIVE_CONTEXT = "❺"  # 攻击性语境

class TKIStrategy(Enum):
    """TKI策略风格"""
    COLLABORATING = "collaborating"    # 协作型
    ACCOMMODATING = "accommodating"    # 迁就型
    COMPETING = "competing"            # 竞争型
    COMPROMISING = "compromising"      # 妥协型
    AVOIDING = "avoiding"              # 回避型

@dataclass
class ConversationContext:
    """对话上下文"""
    recent_messages: List[Dict[str, str]]  # 最近的消息列表
    trigger_type: TriggerType
    strategy: TKIStrategy
    female_speaker: Optional[str] = None
    male_speakers: List[str] = None
    topic: Optional[str] = None

class GPTPromptGenerator:
    """GPT提示生成器"""
    
    def __init__(self):
        self.trigger_descriptions = self._initialize_trigger_descriptions()
        self.strategy_descriptions = self._initialize_strategy_descriptions()
        self.examples = self._initialize_examples()
    
    def _initialize_trigger_descriptions(self) -> Dict[TriggerType, str]:
        """初始化触发类型描述"""
        return {
            TriggerType.FEMALE_INTERRUPTED: "Female speaker was interrupted mid-sentence",
            TriggerType.FEMALE_IGNORED: "Female speaker gave a viewpoint but was ignored",
            TriggerType.MALE_DOMINANCE: "Male speakers dominating the conversation",
            TriggerType.EXPRESSION_DIFFICULTY: "Female speaker showing expression difficulty",
            TriggerType.AGGRESSIVE_CONTEXT: "Aggressive or dismissive context detected"
        }
    
    def _initialize_strategy_descriptions(self) -> Dict[TKIStrategy, str]:
        """初始化策略描述"""
        return {
            TKIStrategy.COLLABORATING: "Collaborating - Integrate perspectives, promote consensus",
            TKIStrategy.ACCOMMODATING: "Accommodating - Prioritize harmony, gentle support",
            TKIStrategy.COMPETING: "Competing - Strongly defend female expression rights",
            TKIStrategy.COMPROMISING: "Compromising - Set fair discussion mechanisms",
            TKIStrategy.AVOIDING: "Avoiding - Divert conflict topics, maintain surface harmony"
        }
    
    def _initialize_examples(self) -> List[Dict]:
        """初始化示例"""
        return [
            {
                "trigger": TriggerType.FEMALE_INTERRUPTED,
                "strategy": TKIStrategy.COMPETING,
                "context": [
                    {"speaker": "Alex", "message": "马龙的反手太稳定了"},
                    {"speaker": "Lily", "message": "我觉得王楚钦的..."},
                    {"speaker": "Zack", "message": "不对，应该是这样"}
                ],
                "intervention": "Let's let her finish—everyone deserves a chance to speak."
            },
            {
                "trigger": TriggerType.FEMALE_IGNORED,
                "strategy": TKIStrategy.COMPROMISING,
                "context": [
                    {"speaker": "Alex", "message": "这个战术很有效"},
                    {"speaker": "Lily", "message": "我觉得我们可以考虑观众反馈"},
                    {"speaker": "Zack", "message": "继续讨论技术实现"}
                ],
                "intervention": "Maybe we can take turns sharing opinions? Lily had a good point about audience feedback."
            },
            {
                "trigger": TriggerType.MALE_DOMINANCE,
                "strategy": TKIStrategy.COLLABORATING,
                "context": [
                    {"speaker": "Alex", "message": "这个分析很准确"},
                    {"speaker": "Zack", "message": "完全同意"},
                    {"speaker": "Alex", "message": "从技术角度分析..."}
                ],
                "intervention": "Both perspectives are valuable. Let's hear from everyone to get a complete picture."
            },
            {
                "trigger": TriggerType.EXPRESSION_DIFFICULTY,
                "strategy": TKIStrategy.ACCOMMODATING,
                "context": [
                    {"speaker": "Lily", "message": "我觉得...也许..."},
                    {"speaker": "Lily", "message": "不太确定，但是..."}
                ],
                "intervention": "Take your time, Lily. Your thoughts are important to us."
            },
            {
                "trigger": TriggerType.AGGRESSIVE_CONTEXT,
                "strategy": TKIStrategy.COMPETING,
                "context": [
                    {"speaker": "Lily", "message": "这个想法很有创意"},
                    {"speaker": "Alex", "message": "你懂什么？你只是看脸"}
                ],
                "intervention": "This gender bias is wrong. Everyone has equal rights to express themselves."
            }
        ]
    
    def generate_prompt(self, context: ConversationContext) -> str:
        """生成GPT提示"""
        
        # 构建上下文消息
        context_messages = self._format_context_messages(context.recent_messages)
        
        # 获取相关示例
        relevant_examples = self._get_relevant_examples(context.trigger_type, context.strategy)
        
        # 构建完整提示
        prompt = f"""Task: Generate a 1–2 sentence chatbot intervention.

Context (last {len(context.recent_messages)} messages in the group chat):
{context_messages}

Trigger: {context.trigger_type.value} – {self.trigger_descriptions[context.trigger_type]}
Conflict Style: {context.strategy.value.title()}

{self.strategy_descriptions[context.strategy]}

Examples:
{self._format_examples(relevant_examples)}

Your turn:
Generate a natural, conversational intervention that:
1. Addresses the specific trigger situation
2. Uses the specified conflict management style
3. Sounds natural and human-like
4. Is 1-2 sentences maximum
5. Maintains the conversation flow

Intervention:"""

        return prompt
    
    def _format_context_messages(self, messages: List[Dict[str, str]]) -> str:
        """格式化上下文消息"""
        formatted = []
        for msg in messages:
            speaker = msg.get('speaker', 'Unknown')
            message = msg.get('message', '')
            formatted.append(f"{speaker}: {message}")
        return "\n".join(formatted)
    
    def _get_relevant_examples(self, trigger_type: TriggerType, strategy: TKIStrategy) -> List[Dict]:
        """获取相关示例"""
        relevant = []
        
        # 优先选择完全匹配的示例
        for example in self.examples:
            if example['trigger'] == trigger_type and example['strategy'] == strategy:
                relevant.append(example)
        
        # 如果没有完全匹配，选择相同触发类型的示例
        if not relevant:
            for example in self.examples:
                if example['trigger'] == trigger_type:
                    relevant.append(example)
        
        # 如果还是没有，选择相同策略的示例
        if not relevant:
            for example in self.examples:
                if example['strategy'] == strategy:
                    relevant.append(example)
        
        # 最多返回2个示例
        return relevant[:2]
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """格式化示例"""
        formatted = []
        for i, example in enumerate(examples, 1):
            context = self._format_context_messages(example['context'])
            formatted.append(f"""Example {i}:
Trigger: {example['trigger'].value} {self.trigger_descriptions[example['trigger']]}
Style: {example['strategy'].value.title()}
Context:
{context}
Chatbot: "{example['intervention']}" """)
        
        return "\n".join(formatted)
    
    def create_context_from_detection(self, 
                                    recent_messages: List[Dict[str, str]],
                                    trigger_type: str,
                                    strategy: str,
                                    **kwargs) -> ConversationContext:
        """从检测结果创建上下文"""
        
        # 转换触发类型
        trigger_map = {
            'female_interrupted': TriggerType.FEMALE_INTERRUPTED,
            'silence_after_female': TriggerType.FEMALE_IGNORED,
            'male_consecutive': TriggerType.MALE_DOMINANCE,
            'expression_difficulty': TriggerType.EXPRESSION_DIFFICULTY,
            'aggressive_context': TriggerType.AGGRESSIVE_CONTEXT
        }
        
        # 转换策略
        strategy_map = {
            'collaborating': TKIStrategy.COLLABORATING,
            'accommodating': TKIStrategy.ACCOMMODATING,
            'competing': TKIStrategy.COMPETING,
            'compromising': TKIStrategy.COMPROMISING,
            'avoiding': TKIStrategy.AVOIDING
        }
        
        return ConversationContext(
            recent_messages=recent_messages,
            trigger_type=trigger_map.get(trigger_type, TriggerType.FEMALE_IGNORED),
            strategy=strategy_map.get(strategy, TKIStrategy.COMPROMISING),
            female_speaker=kwargs.get('female_speaker'),
            male_speakers=kwargs.get('male_speakers', []),
            topic=kwargs.get('topic')
        )
    
    def get_prompt_template_info(self) -> Dict:
        """获取提示模板信息"""
        return {
            "trigger_types": {t.value: self.trigger_descriptions[t] for t in TriggerType},
            "strategies": {s.value: self.strategy_descriptions[s] for s in TKIStrategy},
            "example_count": len(self.examples),
            "description": "GPT提示生成器，用于生成符合TKI风格的插话内容"
        } 