"""
增强版GPT-4冲突检测系统 - 支持单人和多人对话分析
"""

import asyncio
import os
import logging
from datetime import datetime
from collections import deque
from enum import Enum
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TKIStrategy(Enum):
    """TKI干预策略"""
    COLLABORATING = "协作"
    ACCOMMODATING = "迁就"
    COMPETING = "竞争"
    AVOIDING = "回避"
    COMPROMISING = "妥协"

class ConflictLevel(Enum):
    """冲突等级"""
    NONE = "无冲突"
    MILD = "轻微分歧"
    MODERATE = "中等冲突"
    HIGH = "严重冲突"
    CRITICAL = "危险冲突"

class AnalysisMode(Enum):
    """分析模式"""
    SINGLE_SPEAKER = "单人模式"
    MULTI_SPEAKER = "多人对话"
    WAITING = "等待更多参与者"

@dataclass
class ConversationTurn:
    """对话轮次"""
    speaker: str
    content: str
    timestamp: datetime
    turn_number: int

@dataclass
class LLMAnalysisResult:
    """LLM分析结果"""
    conflict_score: float
    conflict_level: ConflictLevel
    conflict_type: str
    emotional_tone: str
    escalation_risk: float
    recommended_strategy: TKIStrategy
    intervention_message: str
    analysis_reasoning: str
    should_intervene: bool
    analysis_mode: AnalysisMode

class SmartGPT4Analyzer:
    """智能GPT-4分析器 - 支持单人和多人模式"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.conversation_history = deque(maxlen=15)
        self.unique_speakers: Set[str] = set()
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    async def analyze_conversation(self, new_speaker: str, new_message: str) -> LLMAnalysisResult:
        """智能分析对话"""
        
        logger.info(f"接收到消息: {new_speaker}: {new_message}")
        
        # 添加新消息到历史
        turn = ConversationTurn(
            speaker=new_speaker,
            content=new_message,
            timestamp=datetime.now(),
            turn_number=len(self.conversation_history) + 1
        )
        self.conversation_history.append(turn)
        self.unique_speakers.add(new_speaker)
        
        # 智能决定分析模式
        analysis_mode = self._determine_analysis_mode()
        
        if analysis_mode == AnalysisMode.WAITING:
            return LLMAnalysisResult(
                conflict_score=0.0,
                conflict_level=ConflictLevel.NONE,
                conflict_type="等待更多参与者",
                emotional_tone="中性",
                escalation_risk=0.0,
                recommended_strategy=TKIStrategy.COLLABORATING,
                intervention_message="",
                analysis_reasoning="单人对话，等待其他参与者加入或更多消息",
                should_intervene=False,
                analysis_mode=analysis_mode
            )
        else:
            return await self._call_gpt4_analysis(analysis_mode)
    
    def _determine_analysis_mode(self) -> AnalysisMode:
        """智能确定分析模式"""
        
        # 如果只有1个人且消息少于3条，等待
        if len(self.unique_speakers) == 1 and len(self.conversation_history) < 3:
            return AnalysisMode.WAITING
        
        # 如果有多个参与者，立即分析
        if len(self.unique_speakers) > 1:
            return AnalysisMode.MULTI_SPEAKER
        
        # 如果单人但消息较多，也进行分析（可能是自我冲突或压力表达）
        if len(self.unique_speakers) == 1 and len(self.conversation_history) >= 3:
            return AnalysisMode.SINGLE_SPEAKER
        
        return AnalysisMode.WAITING
    
    async def _call_gpt4_analysis(self, mode: AnalysisMode) -> LLMAnalysisResult:
        """调用GPT-4进行分析"""
        
        conversation_text = self._format_conversation_for_llm()
        logger.info(f"分析模式: {mode.value}, 对话: {conversation_text}")
        
        # 根据模式调整系统提示
        if mode == AnalysisMode.SINGLE_SPEAKER:
            system_prompt = """你是冲突检测专家。当前是单人对话模式，重点分析：
1. 个人压力和挫败感表达
2. 时间紧迫感和焦虑
3. 对他人的不满或抱怨
4. 重复性的担忧或问题
5. 情绪升级的迹象

单人对话中的冲突信号包括：
- 反复提及同一问题
- 表达时间压力或deadline焦虑
- 对他人行为的抱怨
- 情绪化的表达
- 寻求确认或支持的迫切需求

请严格按照JSON格式回复：
{
    "conflict_score": 数值0-1,
    "conflict_level": "无冲突/轻微分歧/中等冲突/严重冲突/危险冲突",
    "conflict_type": "冲突类型描述",
    "emotional_tone": "情绪描述",
    "escalation_risk": 数值0-1,
    "recommended_strategy": "协作/迁就/竞争/回避/妥协",
    "should_intervene": true或false,
    "intervention_message": "干预消息",
    "analysis_reasoning": "分析原因"
}"""
        else:
            system_prompt = """你是冲突检测专家。当前是多人对话模式，重点分析：
1. 参与者之间的直接冲突
2. 间接的不满和暗示
3. 责任推卸和相互指责
4. 情绪在参与者间的传播
5. 群体动力学问题

多人对话中的冲突信号包括：
- 不同观点的碰撞
- 相互指责或责备
- 防御性回应
- 权力斗争
- 沟通失效

请严格按照JSON格式回复：
{
    "conflict_score": 数值0-1,
    "conflict_level": "无冲突/轻微分歧/中等冲突/严重冲突/危险冲突",
    "conflict_type": "冲突类型描述",
    "emotional_tone": "情绪描述",
    "escalation_risk": 数值0-1,
    "recommended_strategy": "协作/迁就/竞争/回避/妥协",
    "should_intervene": true或false,
    "intervention_message": "干预消息",
    "analysis_reasoning": "分析原因"
}"""

        user_prompt = f"分析以下对话的冲突程度（{mode.value}）：\n\n{conversation_text}"

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
                'max_tokens': 800
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"GPT-4 API error: {response.status} - {error_text}")
                        return self._create_fallback_result(f"API错误: {response.status}", mode)
                    
                    result = await response.json()
                    
                    if 'choices' not in result or not result['choices']:
                        logger.error("GPT-4 API returned no choices")
                        return self._create_fallback_result("API返回为空", mode)
                    
                    gpt_response = result['choices'][0]['message']['content'].strip()
                    logger.info(f"GPT-4原始回复: {gpt_response}")
                    
                    return self._parse_gpt4_response(gpt_response, mode)
                    
        except Exception as e:
            logger.error(f"GPT-4 API call failed: {e}")
            return self._create_fallback_result(f"API错误: {str(e)}", mode)
    
    def _format_conversation_for_llm(self) -> str:
        """格式化对话供LLM分析"""
        conversation_lines = []
        
        for turn in self.conversation_history:
            conversation_lines.append(f"{turn.speaker}: {turn.content}")
        
        return "\n".join(conversation_lines)
    
    def _parse_gpt4_response(self, response: str, mode: AnalysisMode) -> LLMAnalysisResult:
        """解析GPT-4的JSON响应"""
        try:
            # 多种方式尝试解析JSON
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
                if json_start != -1 and json_end > json_start:
                    try:
                        data = json.loads(response[json_start:json_end])
                    except json.JSONDecodeError:
                        pass
            
            # 尝试清理markdown
            if data is None:
                import re
                cleaned = re.sub(r'```json\s*|\s*```', '', response).strip()
                try:
                    data = json.loads(cleaned)
                except json.JSONDecodeError:
                    pass
            
            if data is None:
                logger.error(f"无法解析GPT-4响应为JSON: {response}")
                return self._create_fallback_result("JSON解析失败", mode)
            
            # 映射枚举值
            level_map = {
                "无冲突": ConflictLevel.NONE,
                "轻微分歧": ConflictLevel.MILD,
                "中等冲突": ConflictLevel.MODERATE,
                "严重冲突": ConflictLevel.HIGH,
                "危险冲突": ConflictLevel.CRITICAL
            }
            
            strategy_map = {
                "协作": TKIStrategy.COLLABORATING,
                "迁就": TKIStrategy.ACCOMMODATING,
                "竞争": TKIStrategy.COMPETING,
                "回避": TKIStrategy.AVOIDING,
                "妥协": TKIStrategy.COMPROMISING
            }
            
            return LLMAnalysisResult(
                conflict_score=float(data.get('conflict_score', 0.0)),
                conflict_level=level_map.get(data.get('conflict_level', '无冲突'), ConflictLevel.NONE),
                conflict_type=data.get('conflict_type', '未知'),
                emotional_tone=data.get('emotional_tone', '中性'),
                escalation_risk=float(data.get('escalation_risk', 0.0)),
                recommended_strategy=strategy_map.get(data.get('recommended_strategy', '协作'), TKIStrategy.COLLABORATING),
                intervention_message=data.get('intervention_message', ''),
                analysis_reasoning=data.get('analysis_reasoning', ''),
                should_intervene=bool(data.get('should_intervene', False)),
                analysis_mode=mode
            )
            
        except Exception as e:
            logger.error(f"解析GPT-4响应失败: {e}")
            return self._create_fallback_result(f"解析错误: {str(e)}", mode)
    
    def _create_fallback_result(self, error_reason: str, mode: AnalysisMode) -> LLMAnalysisResult:
        """创建降级结果"""
        return LLMAnalysisResult(
            conflict_score=0.0,
            conflict_level=ConflictLevel.NONE,
            conflict_type="分析失败",
            emotional_tone="未知",
            escalation_risk=0.0,
            recommended_strategy=TKIStrategy.COLLABORATING,
            intervention_message="",
            analysis_reasoning=f"GPT-4分析失败: {error_reason}",
            should_intervene=False,
            analysis_mode=mode
        )

# 全局分析器
smart_analyzer = SmartGPT4Analyzer()
message_count = 0

def format_score_bar(score: float, width: int = 10) -> str:
    """格式化分数条形图"""
    filled = int(score * width)
    return "█" * filled + "░" * (width - filled)

def get_color_indicator(score: float) -> str:
    """获取颜色指示器"""
    if score >= 0.8:
        return "🔴"
    elif score >= 0.6:
        return "🟠"
    elif score >= 0.4:
        return "🟡"
    elif score >= 0.2:
        return "🟢"
    else:
        return "⚪"

def get_mode_icon(mode: AnalysisMode) -> str:
    """获取模式图标"""
    icons = {
        AnalysisMode.SINGLE_SPEAKER: "👤",
        AnalysisMode.MULTI_SPEAKER: "👥",
        AnalysisMode.WAITING: "⏳"
    }
    return icons.get(mode, "❓")

def print_startup_banner():
    """打印启动横幅"""
    start_time = datetime.now()
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                🤖 智能GPT-4冲突检测机器人 - 单人/多人自适应 v3.0                      ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ 启动时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}                                                ║
║ 分析引擎: 🧠 GPT-4 (自适应模式)                                                    ║
║ 支持模式: 👤单人压力检测 | 👥多人冲突分析 | ⏳智能等待                               ║
║                                                                              ║
║ 单人模式: 压力表达 | 时间焦虑 | 重复担忧 | 情绪升级                                   ║
║ 多人模式: 直接冲突 | 相互指责 | 防御回应 | 群体动力                                   ║
║ 图例: 🚨=干预 ✅=正常 👤👥⏳=模式 🔴🟠🟡🟢⚪=等级                                 ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

async def log_smart_analysis(message: str, author: str, result: LLMAnalysisResult, processing_time: float):
    """记录智能分析结果"""
    global message_count
    message_count += 1
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    status = "🚨" if result.should_intervene else "✅"
    mode_icon = get_mode_icon(result.analysis_mode)
    
    message_preview = message[:40] + "..." if len(message) > 40 else message
    if not message.strip():
        message_preview = "[空消息]"
    
    score_bar = format_score_bar(result.conflict_score)
    color_indicator = get_color_indicator(result.conflict_score)
    
    # 显示参与者信息
    speaker_count = len(smart_analyzer.unique_speakers)
    speakers_info = f"参与者: {speaker_count}人 ({', '.join(smart_analyzer.unique_speakers)})"
    
    print(f"""
{status} [{timestamp}] {author} (轮次#{message_count}) {mode_icon}
📝 {message_preview}
👥 {speakers_info}
📊 冲突分数: {result.conflict_score:.2f} {score_bar} {color_indicator}
🔍 冲突类型: {result.conflict_type}
😊 情绪色调: {result.emotional_tone}
📈 升级风险: {result.escalation_risk:.2f}
🎯 推荐策略: {result.recommended_strategy.value}
🧠 分析模式: {result.analysis_mode.value}
⏱️  处理时间: {processing_time:.1f}ms
💭 GPT-4分析: {result.analysis_reasoning}
""".strip())
    
    if result.should_intervene:
        print(f"💬 智能干预: {result.intervention_message}")
    
    print("─" * 70)

class SmartConflictBot:
    """智能冲突检测机器人"""
    
    def __init__(self):
        self.discord_client = None
        
    async def start(self, token: str):
        """启动Discord机器人"""
        import discord
        
        print_startup_banner()
        
        class DiscordBot(discord.Client):
            def __init__(self):
                super().__init__(intents=discord.Intents.default())
                
            async def on_ready(self):
                logger.info(f'🚀 机器人已登录为 {self.user}')
                print(f"\n🌟 {self.user} 已上线，智能分析开始...")
                print("=" * 70)
                
            async def on_message(self, message):
                if message.author == self.user:
                    return
                
                message_content = message.content
                author_name = message.author.display_name
                
                logger.info(f"Discord消息: {author_name}: {message_content}")
                
                start_processing = asyncio.get_event_loop().time()
                
                try:
                    result = await smart_analyzer.analyze_conversation(author_name, message_content)
                    processing_time = (asyncio.get_event_loop().time() - start_processing) * 1000
                    
                    await log_smart_analysis(message_content, author_name, result, processing_time)
                    
                    if result.should_intervene:
                        await message.channel.send(result.intervention_message)
                        
                except Exception as e:
                    logger.error(f"智能分析失败: {e}")
                    print(f"❌ 智能分析失败: {e}")
        
        self.discord_client = DiscordBot()
        await self.discord_client.start(token)

async def main():
    """主函数"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found")
        return
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found")
        print("❌ 请在.env文件中配置OPENAI_API_KEY")
        return
    
    bot = SmartConflictBot()
    
    try:
        logger.info("Starting Smart GPT-4 conflict intervention bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
        print(f"\n🛑 机器人已停止 - 共分析 {message_count} 条消息")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 