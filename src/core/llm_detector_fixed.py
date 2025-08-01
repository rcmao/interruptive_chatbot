"""
修复版的GPT-4冲突检测系统
"""

import asyncio
import os
import logging
from datetime import datetime
from collections import deque
from enum import Enum
from typing import List, Dict, Optional
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

class GPT4ConflictAnalyzer:
    """GPT-4冲突分析器（修复版）"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.conversation_history = deque(maxlen=10)
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    async def analyze_conversation(self, new_speaker: str, new_message: str) -> LLMAnalysisResult:
        """分析对话并返回结果"""
        
        # 调试：打印接收到的消息
        logger.info(f"接收到消息: {new_speaker}: {new_message}")
        
        # 添加新消息到历史
        turn = ConversationTurn(
            speaker=new_speaker,
            content=new_message,
            timestamp=datetime.now(),
            turn_number=len(self.conversation_history) + 1
        )
        self.conversation_history.append(turn)
        
        # 从第2轮开始分析
        if len(self.conversation_history) >= 2:
            return await self._call_gpt4_analysis()
        else:
            return LLMAnalysisResult(
                conflict_score=0.0,
                conflict_level=ConflictLevel.NONE,
                conflict_type="对话刚开始",
                emotional_tone="中性",
                escalation_risk=0.0,
                recommended_strategy=TKIStrategy.COLLABORATING,
                intervention_message="",
                analysis_reasoning="对话轮次不足，继续观察",
                should_intervene=False
            )
    
    async def _call_gpt4_analysis(self) -> LLMAnalysisResult:
        """调用GPT-4进行分析"""
        
        # 构建对话历史
        conversation_text = self._format_conversation_for_llm()
        
        logger.info(f"发送给GPT-4的对话: {conversation_text}")
        
        # 简化的系统提示
        system_prompt = """你是冲突检测专家。分析对话中的冲突程度，包括：
1. 直接攻击性语言
2. 间接不满表达
3. 时间压力和责任推卸
4. 情绪升级趋势

请严格按照以下JSON格式回复（不要添加任何其他内容）：
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

        user_prompt = f"分析以下对话的冲突程度：\n\n{conversation_text}"

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
                'temperature': 0.1,  # 更低温度保证格式一致性
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
                        return self._create_fallback_result(f"API错误: {response.status}")
                    
                    result = await response.json()
                    
                    if 'choices' not in result or not result['choices']:
                        logger.error("GPT-4 API returned no choices")
                        return self._create_fallback_result("API返回为空")
                    
                    # 获取GPT-4的回复
                    gpt_response = result['choices'][0]['message']['content'].strip()
                    logger.info(f"GPT-4原始回复: {gpt_response}")
                    
                    # 解析回复
                    return self._parse_gpt4_response(gpt_response)
                    
        except asyncio.TimeoutError:
            logger.error("GPT-4 API timeout")
            return self._create_fallback_result("API超时")
        except Exception as e:
            logger.error(f"GPT-4 API call failed: {e}")
            return self._create_fallback_result(f"API错误: {str(e)}")
    
    def _format_conversation_for_llm(self) -> str:
        """格式化对话供LLM分析"""
        conversation_lines = []
        
        for turn in self.conversation_history:
            conversation_lines.append(f"{turn.speaker}: {turn.content}")
        
        return "\n".join(conversation_lines)
    
    def _parse_gpt4_response(self, response: str) -> LLMAnalysisResult:
        """解析GPT-4的JSON响应"""
        try:
            # 清理响应文本
            response = response.strip()
            
            # 多种方式尝试提取JSON
            json_str = None
            
            # 方法1: 直接解析
            try:
                json_str = response
                data = json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
            # 方法2: 查找大括号
            if json_str is None:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        json_str = None
            
            # 方法3: 使用正则表达式清理
            if json_str is None:
                import re
                # 移除markdown代码块标记
                cleaned = re.sub(r'```json\s*|\s*```', '', response)
                cleaned = cleaned.strip()
                try:
                    data = json.loads(cleaned)
                    json_str = cleaned
                except json.JSONDecodeError:
                    pass
            
            if json_str is None:
                logger.error(f"无法解析GPT-4响应为JSON: {response}")
                return self._create_fallback_result("JSON解析失败")
            
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
                should_intervene=bool(data.get('should_intervene', False))
            )
            
        except Exception as e:
            logger.error(f"解析GPT-4响应失败: {e}")
            logger.error(f"响应内容: {response}")
            return self._create_fallback_result(f"解析错误: {str(e)}")
    
    def _create_fallback_result(self, error_reason: str) -> LLMAnalysisResult:
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
            should_intervene=False
        )

# 全局分析器
llm_analyzer = GPT4ConflictAnalyzer()
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

def print_startup_banner():
    """打印启动横幅"""
    start_time = datetime.now()
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                  🤖 GPT-4智能冲突检测机器人 - 修复版 v2.0                           ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ 启动时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}                                                ║
║ 分析引擎: 🧠 GPT-4 (温度=0.1, 高稳定性)                                            ║
║ 分析起点: 第2轮对话开始                                                            ║
║ 修复内容: JSON解析 | 消息获取 | 错误处理                                            ║
║                                                                              ║
║ 检测范围: 时间压力 | 责任推卸 | 情绪升级 | 网络用语 | 微妙暗示                        ║
║ 图例: 🚨=干预 ✅=正常 🔴🟠🟡🟢⚪=冲突等级 ████░░=强度条                             ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

async def log_llm_analysis(message: str, author: str, result: LLMAnalysisResult, processing_time: float):
    """记录LLM分析结果"""
    global message_count
    message_count += 1
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    status = "🚨" if result.should_intervene else "✅"
    
    # 确保消息内容正确显示
    message_preview = message[:40] + "..." if len(message) > 40 else message
    if not message.strip():
        message_preview = "[空消息]"
    
    score_bar = format_score_bar(result.conflict_score)
    color_indicator = get_color_indicator(result.conflict_score)
    
    print(f"""
{status} [{timestamp}] {author} (轮次#{message_count})
📝 {message_preview}
📊 冲突分数: {result.conflict_score:.2f} {score_bar} {color_indicator}
🔍 冲突类型: {result.conflict_type}
😊 情绪色调: {result.emotional_tone}
📈 升级风险: {result.escalation_risk:.2f}
🎯 推荐策略: {result.recommended_strategy.value}
⏱️  处理时间: {processing_time:.1f}ms
💭 GPT-4分析: {result.analysis_reasoning}
""".strip())
    
    if result.should_intervene:
        print(f"💬 智能干预: {result.intervention_message}")
    
    print("─" * 70)

class LLMConflictBot:
    """基于LLM的冲突检测机器人（修复版）"""
    
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
                print(f"\n🌟 {self.user} 已上线，GPT-4开始分析...")
                print("=" * 70)
                
            async def on_message(self, message):
                if message.author == self.user:
                    return
                
                # 确保获取到消息内容
                message_content = message.content
                author_name = message.author.display_name
                
                # 调试输出
                logger.info(f"Discord消息: {author_name}: {message_content}")
                
                start_processing = asyncio.get_event_loop().time()
                
                try:
                    # 使用GPT-4分析
                    result = await llm_analyzer.analyze_conversation(author_name, message_content)
                    
                    processing_time = (asyncio.get_event_loop().time() - start_processing) * 1000
                    
                    # 记录分析结果
                    await log_llm_analysis(message_content, author_name, result, processing_time)
                    
                    # 发送干预消息
                    if result.should_intervene:
                        await message.channel.send(result.intervention_message)
                        
                except Exception as e:
                    logger.error(f"LLM分析失败: {e}")
                    print(f"❌ LLM分析失败: {e}")
        
        self.discord_client = DiscordBot()
        await self.discord_client.start(token)

async def main():
    """主函数"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found")
        return
    
    # 检查OpenAI API Key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not found")
        print("❌ 请在.env文件中配置OPENAI_API_KEY")
        return
    
    bot = LLMConflictBot()
    
    try:
        logger.info("Starting GPT-4 powered conflict intervention bot (Fixed)...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
        print(f"\n🛑 机器人已停止 - 共分析 {message_count} 条消息")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 