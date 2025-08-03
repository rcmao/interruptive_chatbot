"""
GPT-4实时对话上下文分析器
基于实时对话上下文进行智能打断评估
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ContextTriggerType(Enum):
    """上下文触发类型"""
    CONFLICT_ESCALATION = "conflict_escalation"      # 冲突升级
    EMOTIONAL_DISTRESS = "emotional_distress"        # 情绪困扰
    COMMUNICATION_BREAKDOWN = "communication_breakdown"  # 沟通中断
    POWER_IMBALANCE = "power_imbalance"             # 权力不平衡
    GENDER_BIAS = "gender_bias"                     # 性别偏见
    EXPRESSION_BLOCKING = "expression_blocking"     # 表达受阻
    TIME_PRESSURE = "time_pressure"                 # 时间压力
    GROUP_DYNAMICS = "group_dynamics"               # 群体动力学

@dataclass
class ContextAnalysisResult:
    """上下文分析结果"""
    should_interrupt: bool
    confidence: float  # 0-1
    trigger_type: ContextTriggerType
    urgency_level: int  # 1-5
    reasoning: str
    suggested_intervention: str
    context_score: float  # 0-1
    emotional_intensity: float  # 0-1
    escalation_risk: float  # 0-1
    timestamp: datetime

class GPT4RealtimeContextAnalyzer:
    """GPT-4实时上下文分析器"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = api_base or os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        # 对话上下文管理
        self.conversation_contexts = {}  # room_id -> context
        self.intervention_history = deque(maxlen=50)
        self.analysis_cache = {}  # 缓存分析结果
        
        # 配置参数
        self.config = {
            'context_window': 10,  # 分析最近10条消息
            'intervention_cooldown': 30,  # 30秒冷却时间
            'high_urgency_threshold': 0.7,  # 高紧急度阈值
            'medium_urgency_threshold': 0.5,  # 中等紧急度阈值
            'low_urgency_threshold': 0.3,  # 低紧急度阈值
            'cache_ttl': 10,  # 缓存10秒
        }
    
    async def analyze_context_and_decide(
        self, 
        room_id: str, 
        new_message: str, 
        author: str, 
        gender: str,
        timestamp: datetime = None
    ) -> ContextAnalysisResult:
        """分析对话上下文并决定是否打断"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # 更新对话上下文
        self._update_conversation_context(room_id, new_message, author, gender, timestamp)
        
        # 检查冷却时间
        if self._is_in_cooldown(room_id):
            return ContextAnalysisResult(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=ContextTriggerType.GROUP_DYNAMICS,
                urgency_level=1,
                reasoning="处于干预冷却期",
                suggested_intervention="",
                context_score=0.0,
                emotional_intensity=0.0,
                escalation_risk=0.0,
                timestamp=timestamp
            )
        
        # 获取对话上下文
        context = self.conversation_contexts.get(room_id, [])
        if len(context) < 2:
            return ContextAnalysisResult(
                should_interrupt=False,
                confidence=0.0,
                trigger_type=ContextTriggerType.GROUP_DYNAMICS,
                urgency_level=1,
                reasoning="对话上下文不足",
                suggested_intervention="",
                context_score=0.0,
                emotional_intensity=0.0,
                escalation_risk=0.0,
                timestamp=timestamp
            )
        
        # 调用GPT-4进行上下文分析
        try:
            analysis_result = await self._call_gpt4_context_analysis(
                context, new_message, author, gender
            )
            
            # 记录干预历史
            if analysis_result.should_interrupt:
                self.intervention_history.append({
                    'room_id': room_id,
                    'timestamp': timestamp,
                    'trigger_type': analysis_result.trigger_type.value,
                    'confidence': analysis_result.confidence
                })
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"GPT-4上下文分析失败: {e}")
            return self._create_fallback_result(timestamp)
    
    def _update_conversation_context(
        self, 
        room_id: str, 
        message: str, 
        author: str, 
        gender: str, 
        timestamp: datetime
    ):
        """更新对话上下文"""
        if room_id not in self.conversation_contexts:
            self.conversation_contexts[room_id] = []
        
        context = self.conversation_contexts[room_id]
        
        # 添加新消息
        context.append({
            'message': message,
            'author': author,
            'gender': gender,
            'timestamp': timestamp
        })
        
        # 保持上下文窗口大小
        if len(context) > self.config['context_window']:
            context.pop(0)
        
        # 清理过期消息（超过5分钟）
        cutoff_time = timestamp - timedelta(minutes=5)
        self.conversation_contexts[room_id] = [
            msg for msg in context 
            if msg['timestamp'] > cutoff_time
        ]
    
    def _is_in_cooldown(self, room_id: str) -> bool:
        """检查是否在冷却期内"""
        recent_interventions = [
            intervention for intervention in self.intervention_history
            if (intervention['room_id'] == room_id and 
                (datetime.now() - intervention['timestamp']).seconds < self.config['intervention_cooldown'])
        ]
        return len(recent_interventions) > 0
    
    async def _call_gpt4_context_analysis(
        self, 
        context: List[Dict], 
        new_message: str, 
        author: str, 
        gender: str
    ) -> ContextAnalysisResult:
        """调用GPT-4进行上下文分析"""
        
        # 构建上下文文本
        context_text = self._format_context_for_analysis(context, new_message, author, gender)
        
        system_prompt = """你是专业的对话冲突检测专家。你的任务是分析实时对话上下文，判断是否需要AI干预来改善沟通质量。

分析重点：
1. 冲突升级迹象：参与者之间的对抗性增强
2. 情绪困扰：明显的挫败感、焦虑或愤怒表达
3. 沟通中断：参与者被忽视、打断或无法表达
4. 权力不平衡：某些参与者主导对话，其他人被边缘化
5. 性别偏见：基于性别的歧视性行为或语言
6. 表达受阻：参与者试图表达但被阻止
7. 时间压力：紧迫感导致的沟通质量下降
8. 群体动力学：群体内部的紧张关系

评估标准：
- 上下文分数(0-1)：基于整体对话氛围
- 情绪强度(0-1)：当前情绪化程度
- 升级风险(0-1)：冲突进一步恶化的可能性
- 紧急度(1-5)：干预的紧迫程度

请严格按照JSON格式回复：
{
    "should_interrupt": true或false,
    "confidence": 0-1之间的数值,
    "trigger_type": "触发类型",
    "urgency_level": 1-5之间的整数,
    "reasoning": "详细分析原因",
    "suggested_intervention": "建议的干预措施",
    "context_score": 0-1之间的数值,
    "emotional_intensity": 0-1之间的数值,
    "escalation_risk": 0-1之间的数值
}"""

        user_prompt = f"分析以下对话上下文，判断是否需要干预：\n\n{context_text}"

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 1000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=15)  # 15秒超时
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"GPT-4 API error: {response.status} - {error_text}")
                        return self._create_fallback_result(datetime.now())
                    
                    result = await response.json()
                    
                    if 'choices' not in result or not result['choices']:
                        logger.error("GPT-4 API returned no choices")
                        return self._create_fallback_result(datetime.now())
                    
                    gpt_response = result['choices'][0]['message']['content'].strip()
                    logger.info(f"GPT-4上下文分析回复: {gpt_response}")
                    
                    return self._parse_gpt4_response(gpt_response, datetime.now())
                    
        except Exception as e:
            logger.error(f"GPT-4上下文分析API调用失败: {e}")
            return self._create_fallback_result(datetime.now())
    
    def _format_context_for_analysis(
        self, 
        context: List[Dict], 
        new_message: str, 
        author: str, 
        gender: str
    ) -> str:
        """格式化上下文供分析"""
        context_lines = []
        
        # 添加历史消息
        for i, msg in enumerate(context):
            context_lines.append(f"{msg['author']}({msg['gender']}): {msg['message']}")
        
        # 添加新消息（标记为当前消息）
        context_lines.append(f"[当前] {author}({gender}): {new_message}")
        
        return "\n".join(context_lines)
    
    def _parse_gpt4_response(self, response: str, timestamp: datetime) -> ContextAnalysisResult:
        """解析GPT-4的JSON响应"""
        try:
            # 尝试解析JSON
            data = None
            
            # 尝试直接解析
            try:
                data = json.loads(response.strip())
            except json.JSONDecodeError:
                pass
            
            # 尝试提取大括号内容
            if data is None:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    try:
                        data = json.loads(response[json_start:json_end])
                    except json.JSONDecodeError:
                        pass
            
            if data is None:
                logger.error(f"无法解析GPT-4响应: {response}")
                return self._create_fallback_result(timestamp)
            
            # 解析触发类型
            trigger_type_str = data.get('trigger_type', 'group_dynamics')
            try:
                trigger_type = ContextTriggerType(trigger_type_str)
            except ValueError:
                trigger_type = ContextTriggerType.GROUP_DYNAMICS
            
            return ContextAnalysisResult(
                should_interrupt=data.get('should_interrupt', False),
                confidence=float(data.get('confidence', 0.0)),
                trigger_type=trigger_type,
                urgency_level=int(data.get('urgency_level', 1)),
                reasoning=data.get('reasoning', '分析失败'),
                suggested_intervention=data.get('suggested_intervention', ''),
                context_score=float(data.get('context_score', 0.0)),
                emotional_intensity=float(data.get('emotional_intensity', 0.0)),
                escalation_risk=float(data.get('escalation_risk', 0.0)),
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"解析GPT-4响应失败: {e}")
            return self._create_fallback_result(timestamp)
    
    def _create_fallback_result(self, timestamp: datetime) -> ContextAnalysisResult:
        """创建降级结果"""
        return ContextAnalysisResult(
            should_interrupt=False,
            confidence=0.0,
            trigger_type=ContextTriggerType.GROUP_DYNAMICS,
            urgency_level=1,
            reasoning="分析服务暂时不可用",
            suggested_intervention="",
            context_score=0.0,
            emotional_intensity=0.0,
            escalation_risk=0.0,
            timestamp=timestamp
        )
    
    def get_analysis_statistics(self) -> Dict:
        """获取分析统计信息"""
        total_analyses = len(self.intervention_history)
        recent_interventions = len([
            intervention for intervention in self.intervention_history
            if (datetime.now() - intervention['timestamp']).seconds < 300  # 最近5分钟
        ])
        
        trigger_counts = {}
        for intervention in self.intervention_history:
            trigger_type = intervention['trigger_type']
            trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1
        
        return {
            'total_analyses': total_analyses,
            'recent_interventions': recent_interventions,
            'trigger_counts': trigger_counts,
            'active_contexts': len(self.conversation_contexts)
        } 