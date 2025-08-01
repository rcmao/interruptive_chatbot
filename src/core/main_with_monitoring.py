"""
带监控功能的智能冲突干预聊天机器人
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_monitoring.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入模块
from src.core.explainable_system import ExplainableInterventionBot

class MonitoringBot:
    """带实时监控的机器人"""
    
    def __init__(self):
        self.intervention_bot = ExplainableInterventionBot()
        self.message_count = 0
        self.intervention_count = 0
        self.conversation_start = datetime.now()
    
    def format_score_bar(self, score: float, width: int = 10) -> str:
        """格式化分数条形图"""
        filled = int(score * width)
        return "█" * filled + "░" * (width - filled)
    
    def log_message_analysis(self, message: str, author: str, result: dict, processing_time: float):
        """记录消息分析结果"""
        self.message_count += 1
        
        # 提取分析结果
        should_intervene = result is not None
        if should_intervene:
            self.intervention_count += 1
        
        # 简化分数提取（从现有系统）
        # 由于当前系统不直接返回分数，我们需要从日志中推断
        estimated_score = 0.6 if should_intervene else 0.2
        
        # 时间戳
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 状态图标
        status = "🚨" if should_intervene else "✅"
        
        # 消息预览
        message_preview = message[:50] + "..." if len(message) > 50 else message
        
        # 分数条形图
        score_bar = self.format_score_bar(estimated_score)
        
        # 格式化日志输出
        monitor_log = f"""
{status} [{timestamp}] {author} (#{self.message_count})
📝 {message_preview}
📊 估计分数: {estimated_score:.2f} {score_bar} | 处理时间: {processing_time:.1f}ms
🎯 干预率: {self.intervention_count}/{self.message_count} ({self.intervention_count/self.message_count*100:.1f}%)
        """.strip()
        
        # 输出到控制台和日志
        print(monitor_log)
        logger.info(f"分析 - {author}: 分数={estimated_score:.2f}, 干预={should_intervene}")
        
        if should_intervene:
            logger.warning(f"🚨 触发干预 #{self.intervention_count}: {result[:100]}...")
        
        print("-" * 60)
    
    async def process_message_with_monitoring(self, message_content: str, author_name: str, channel_id: str):
        """带监控的消息处理"""
        start_time = asyncio.get_event_loop().time()
        
        # 处理消息
        try:
            intervention = await self.intervention_bot.process_message_with_explanation(
                message_content, 
                author_name, 
                channel_id
            )
            
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 记录分析结果
            self.log_message_analysis(message_content, author_name, intervention, processing_time)
            
            return intervention
            
        except Exception as e:
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"处理消息失败: {e}")
            self.log_message_analysis(message_content, author_name, None, processing_time)
            return None
    
    def print_startup_banner(self):
        """打印启动横幅"""
        banner = f"""
╔════════════════════════════════════════════════════════════════════════════════════════╗
║                           🤖 智能冲突检测机器人 - 监控模式                                    ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                                           ║
║ 监控功能: ✅ 已启用                                                                       ║
║ 日志文件: logs/bot_monitoring.log                                                      ║
║                                                                                        ║
║ 图例说明:                                                                               ║
║ 🚨 = 需要干预  ✅ = 正常对话  📝 = 消息内容  📊 = 冲突分数  🎯 = 干预统计                        ║
║ ████████░░ = 分数条形图 (0.0-1.0)                                                      ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("🔥 监控系统已启动")

class IntelligentConflictBotWithMonitoring:
    """带监控功能的智能冲突干预机器人"""
    
    def __init__(self):
        self.monitoring_bot = MonitoringBot()
        self.discord_client = None
        
    async def start(self, token: str):
        """启动Discord机器人"""
        import discord
        
        # 打印启动横幅
        self.monitoring_bot.print_startup_banner()
        
        class DiscordBot(discord.Client):
            def __init__(self, monitoring_bot):
                super().__init__(intents=discord.Intents.default())
                self.monitoring_bot = monitoring_bot
                
            async def on_ready(self):
                logger.info(f'🚀 机器人已登录为 {self.user}')
                print(f"\n🌟 机器人 {self.user} 已上线，开始监控对话...")
                print("=" * 60)
                
            async def on_message(self, message):
                # 忽略机器人自己的消息
                if message.author == self.user:
                    return
                
                # 带监控的消息处理
                intervention = await self.monitoring_bot.process_message_with_monitoring(
                    message.content, 
                    message.author.display_name, 
                    str(message.channel.id)
                )
                
                if intervention:
                    await message.channel.send(intervention)
        
        # 创建并启动Discord客户端
        self.discord_client = DiscordBot(self.monitoring_bot)
        await self.discord_client.start(token)

async def main():
    """主函数"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found")
        return
    
    bot = IntelligentConflictBotWithMonitoring()
    
    try:
        logger.info("Starting intelligent conflict intervention bot with monitoring...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 