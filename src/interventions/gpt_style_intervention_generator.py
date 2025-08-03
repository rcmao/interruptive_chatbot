"""
GPT风格干预生成器 - 基于聊天上下文和admin选择的风格生成插话
将聊天上下文 + 插话时机 + 所选风格 + 示例合并成一个prompt，让GPT按照指定风格生成插话
"""

import asyncio
import json
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

class InterventionTrigger(Enum):
    """干预触发类型"""
    FEMALE_INTERRUPTED = "female_interrupted"      # 女性被打断
    FEMALE_IGNORED = "female_ignored"              # 女性被忽视
    MALE_DOMINANCE = "male_dominance"              # 男性主导对话
    MALE_CONSECUTIVE = "male_consecutive"          # 男性连续发言
    GENDER_IMBALANCE = "gender_imbalance"          # 性别不平衡
    EXPRESSION_DIFFICULTY = "expression_difficulty"  # 表达困难
    AGGRESSIVE_CONTEXT = "aggressive_context"      # 攻击性语境

@dataclass
class GPTInterventionContext:
    """GPT干预上下文"""
    trigger_type: InterventionTrigger
    urgency_level: int  # 1-5
    confidence: float  # 0-1
    recent_messages: List[Dict]  # 最近的聊天记录
    female_participants: List[str]
    male_participants: List[str]
    current_topic: Optional[str] = None
    admin_style: AdminInterventionStyle = AdminInterventionStyle.AUTO
    max_context_length: int = 10  # 最大上下文长度

class GPTStyleInterventionGenerator:
    """GPT风格干预生成器"""
    
    def __init__(self):
        self.style_examples = self._initialize_style_examples()
        self.trigger_descriptions = self._initialize_trigger_descriptions()
        
    def _initialize_style_examples(self) -> Dict[AdminInterventionStyle, Dict[str, List[str]]]:
        """初始化风格示例"""
        return {
            AdminInterventionStyle.COLLABORATING: {
                "description": "协作型风格：促进合作，整合不同观点，推动共识。语气尊重、逻辑、整合。",
                "examples": [
                    "让我们给{女性用户}一个完整表达的机会，她的观点很有价值。",
                    "我注意到{女性用户}刚才想说什么，让我们听听她的想法？",
                    "每个观点都值得认真对待，{女性用户}请继续。",
                    "让我们保持建设性的讨论氛围，每个人都有表达的权利。",
                    "这个话题很有趣，{女性用户}你有什么看法？"
                ]
            },
            AdminInterventionStyle.ACCOMMODATING: {
                "description": "迁就型风格：关系优先，安抚他人，减少冲突。语气温和、支持、理解。",
                "examples": [
                    "她就是挺喜欢这个话题的～每个人表达方式不一样嘛。",
                    "没关系，慢慢说，我们理解你想表达的意思。",
                    "你的观点很有价值，让我们一起来完善这个想法？",
                    "大家都有表达的权利，让我们保持友好的讨论氛围。",
                    "慢慢表达，我们都在听。"
                ]
            },
            AdminInterventionStyle.COMPETING: {
                "description": "竞争型风格：立场鲜明，为女性据理力争。语气直接、坚定、保护。",
                "examples": [
                    "别因为她是女生就否定她的分析，她说得很专业，你听听再评价吧。",
                    "让她说完，每个人都有平等的表达权利。",
                    "你的观点很有道理，但请让{女性用户}也说完她的想法。",
                    "打断别人是不礼貌的，{女性用户}请继续。",
                    "每个人都有发言权，请尊重{女性用户}的表达。"
                ]
            },
            AdminInterventionStyle.COMPROMISING: {
                "description": "妥协型风格：寻求平衡，各让一步。语气平衡、中立、调和。",
                "examples": [
                    "让我们给每个人平等的表达机会，{女性用户}你想说什么？",
                    "这个话题大家都很关心，让我们轮流发言。",
                    "每个观点都有价值，让我们听听{女性用户}的看法。",
                    "让我们保持讨论的平衡，{女性用户}请继续。",
                    "每个人都有表达的权利，让我们给{女性用户}一个机会。"
                ]
            },
            AdminInterventionStyle.AVOIDING: {
                "description": "回避型风格：避免冲突，转移话题。语气轻松、缓和、转移。",
                "examples": [
                    "我们聊点轻松的吧？这个话题太严肃了。",
                    "让我们换个话题，{女性用户}你觉得呢？",
                    "这个话题很有趣，但我们可以聊点别的。",
                    "让我们保持轻松的氛围，{女性用户}有什么想法？",
                    "我们聊点别的吧，这个话题太复杂了。"
                ]
            }
        }
    
    def _initialize_trigger_descriptions(self) -> Dict[InterventionTrigger, str]:
        """初始化触发类型描述"""
        return {
            InterventionTrigger.FEMALE_INTERRUPTED: "检测到女性用户被打断，需要保护其表达权利",
            InterventionTrigger.FEMALE_IGNORED: "检测到女性用户发言后无人回应，需要鼓励其继续表达",
            InterventionTrigger.MALE_DOMINANCE: "检测到男性主导对话，需要平衡参与度",
            InterventionTrigger.MALE_CONSECUTIVE: "检测到男性连续发言，需要给女性表达机会",
            InterventionTrigger.GENDER_IMBALANCE: "检测到性别参与度不平衡，需要调整",
            InterventionTrigger.EXPRESSION_DIFFICULTY: "检测到表达困难，需要支持和鼓励",
            InterventionTrigger.AGGRESSIVE_CONTEXT: "检测到攻击性语境，需要缓和氛围"
        }
    
    def _format_conversation_context(self, recent_messages: List[Dict], max_length: int = 10) -> str:
        """格式化对话上下文"""
        if not recent_messages:
            return "无对话历史"
        
        # 只取最近的几条消息
        recent = recent_messages[-max_length:]
        
        formatted_messages = []
        for msg in recent:
            timestamp = msg.get('timestamp', '').strftime('%H:%M:%S') if hasattr(msg.get('timestamp', ''), 'strftime') else ''
            author = msg.get('author', 'Unknown')
            message = msg.get('message', '')
            gender = msg.get('gender', 'unknown')
            
            formatted_messages.append(f"[{timestamp}] {author} ({gender}): {message}")
        
        return "\n".join(formatted_messages)
    
    def _build_gpt_prompt(self, context: GPTInterventionContext) -> str:
        """构建GPT提示词"""
        
        # 格式化对话上下文
        conversation_context = self._format_conversation_context(
            context.recent_messages, 
            context.max_context_length
        )
        
        # 获取触发类型描述
        trigger_description = self.trigger_descriptions.get(context.trigger_type, "检测到需要干预的情况")
        
        # 确定使用的风格
        style = self._determine_style(context)
        style_info = self.style_examples.get(style, self.style_examples[AdminInterventionStyle.COLLABORATING])
        
        # 构建风格示例
        style_examples = "\n".join([f"- {example}" for example in style_info["examples"]])
        
        # 替换示例中的占位符
        if context.female_participants:
            style_examples = style_examples.replace("{女性用户}", context.female_participants[0])
        if context.male_participants:
            style_examples = style_examples.replace("{男性用户}", context.male_participants[0])
        
        # 构建完整提示词
        prompt = f"""
你是一个智能聊天机器人，负责在群聊中适时插话，促进健康的讨论氛围。

## 当前对话上下文：
{conversation_context}

## 插话时机：
{trigger_description}
- 紧急程度：{context.urgency_level}/5
- 置信度：{context.confidence:.2f}

## 要求的风格：
{style_info["description"]}

## 风格示例：
{style_examples}

## 任务要求：
请根据上述对话上下文和插话时机，按照指定的风格生成一句自然的插话。要求：
1. 符合指定的风格特点
2. 针对当前对话上下文
3. 自然流畅，不突兀
4. 长度适中（1-2句话）
5. 不要重复已有的示例，要创造性地表达

请直接返回插话内容，不要包含任何解释或标记。
"""
        
        return prompt.strip()
    
    def _determine_style(self, context: GPTInterventionContext) -> AdminInterventionStyle:
        """确定使用的风格"""
        
        # 如果admin设置了特定风格且不是auto，使用admin设置的风格
        if context.admin_style != AdminInterventionStyle.AUTO:
            return context.admin_style
        
        # 否则根据触发类型和紧急程度自动选择
        if context.urgency_level >= 5:
            return AdminInterventionStyle.COMPETING
        elif context.urgency_level >= 4:
            if context.trigger_type in [InterventionTrigger.FEMALE_INTERRUPTED, InterventionTrigger.AGGRESSIVE_CONTEXT]:
                return AdminInterventionStyle.COMPETING
            else:
                return AdminInterventionStyle.COLLABORATING
        elif context.urgency_level >= 3:
            return AdminInterventionStyle.COMPROMISING
        else:
            return AdminInterventionStyle.AVOIDING
    
    async def generate_intervention(self, context: GPTInterventionContext) -> str:
        """生成干预消息"""
        
        # 构建GPT提示词
        prompt = self._build_gpt_prompt(context)
        
        # 调用GPT生成回复（这里使用模拟实现）
        intervention = await self._call_gpt(prompt)
        
        return intervention
    
    async def _call_gpt(self, prompt: str) -> str:
        """调用GPT生成回复"""
        
        import os
        import aiohttp
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 获取API配置
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        if not api_key:
            logger.warning("OPENAI_API_KEY not found, using fallback response")
            return self._get_fallback_response(prompt)
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4',
                'messages': [
                    {'role': 'system', 'content': '你是一个智能聊天机器人，负责在群聊中适时插话，促进健康的讨论氛围。请直接返回插话内容，不要包含任何解释或标记。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,  # 适中的创造性
                'max_tokens': 150,   # 限制长度
                'top_p': 0.9
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{base_url}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)  # 10秒超时
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"GPT API error: {response.status} - {error_text}")
                        return self._get_fallback_response(prompt)
                    
                    result = await response.json()
                    
                    if 'choices' not in result or not result['choices']:
                        logger.error("GPT API returned no choices")
                        return self._get_fallback_response(prompt)
                    
                    gpt_response = result['choices'][0]['message']['content'].strip()
                    logger.info(f"GPT干预生成回复: {gpt_response}")
                    
                    return gpt_response
                    
        except Exception as e:
            logger.error(f"GPT API调用失败: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """获取备用回复"""
        
        # 基于关键词的简单规则生成
        if "女性" in prompt or "female" in prompt.lower():
            if "打断" in prompt or "interrupted" in prompt.lower():
                return "让她说完，每个人都有平等的表达权利。"
            elif "忽视" in prompt or "ignored" in prompt.lower():
                return "我注意到你想说什么，让我们听听你的想法？"
            else:
                return "让我们给每个人平等的表达机会。"
        elif "攻击" in prompt or "aggressive" in prompt.lower():
            return "让我们保持建设性的讨论氛围，每个人都有表达的权利。"
        elif "表达困难" in prompt or "difficulty" in prompt.lower():
            return "慢慢说，我们在听。你想表达的是...？"
        else:
            return "让我们继续建设性的讨论。"
    
    def get_style_info(self, style: AdminInterventionStyle) -> Dict:
        """获取风格信息"""
        style_info = self.style_examples.get(style, {})
        return {
            "name": style.value,
            "description": style_info.get("description", ""),
            "examples": style_info.get("examples", [])
        }
    
    def get_all_styles_info(self) -> Dict:
        """获取所有风格信息"""
        return {
            style.value: self.get_style_info(style)
            for style in AdminInterventionStyle
            if style != AdminInterventionStyle.AUTO
        } 