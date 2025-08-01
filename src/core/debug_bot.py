"""
调试版机器人 - 专门诊断消息获取问题
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/debug_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_debug_banner():
    """打印调试横幅"""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                          🔍 Discord消息获取调试模式                                 ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                                ║
║ 调试目标: 诊断消息内容获取问题                                                       ║
║ 日志级别: DEBUG                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

class DebugBot:
    """调试机器人"""
    
    def __init__(self):
        self.discord_client = None
        self.message_count = 0
        
    async def start(self, token: str):
        """启动调试机器人"""
        import discord
        
        print_debug_banner()
        
        # 设置更完整的intents
        intents = discord.Intents.default()
        intents.message_content = True  # 重要：需要消息内容权限
        intents.messages = True
        intents.guilds = True
        
        class DebugDiscordBot(discord.Client):
            def __init__(self, debug_bot):
                super().__init__(intents=intents)
                self.debug_bot = debug_bot
                
            async def on_ready(self):
                logger.info(f'🚀 调试机器人已登录为 {self.user}')
                print(f"\n🌟 {self.user} 已上线，开始调试...")
                print(f"📋 机器人权限: {self.user.bot}")
                print(f"🔑 Intents配置: message_content={intents.message_content}, messages={intents.messages}")
                print("=" * 70)
                
            async def on_message(self, message):
                self.debug_bot.message_count += 1
                
                print(f"\n🔍 调试信息 #{self.debug_bot.message_count}")
                print(f"   作者: {message.author}")
                print(f"   作者名: {message.author.display_name}")
                print(f"   作者ID: {message.author.id}")
                print(f"   是否为机器人: {message.author.bot}")
                print(f"   消息类型: {type(message.content)}")
                print(f"   消息长度: {len(message.content)}")
                print(f"   原始内容: '{message.content}'")
                print(f"   内容repr: {repr(message.content)}")
                print(f"   频道: {message.channel}")
                print(f"   时间戳: {message.created_at}")
                
                # 忽略机器人自己的消息
                if message.author == self.user:
                    print("   ⏭️  跳过：机器人自己的消息")
                    return
                
                # 检查消息内容
                if not message.content:
                    print("   ❌ 警告：消息内容为空！")
                    print(f"   📎 附件: {len(message.attachments)} 个")
                    print(f"   🏷️  嵌入: {len(message.embeds)} 个")
                    print(f"   😀 反应: {len(message.reactions)} 个")
                else:
                    print(f"   ✅ 消息内容正常: '{message.content[:50]}...'")
                
                # 简单回复测试
                if message.content.strip():
                    try:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        reply = f"[{timestamp}] 收到消息: '{message.content[:30]}...' (长度: {len(message.content)})"
                        await message.channel.send(reply)
                        print(f"   📤 已回复: {reply}")
                    except Exception as e:
                        print(f"   ❌ 回复失败: {e}")
                
                print("-" * 50)
        
        self.discord_client = DebugDiscordBot(self)
        await self.discord_client.start(token)

async def main():
    """主函数"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found")
        return
    
    bot = DebugBot()
    
    try:
        logger.info("Starting debug bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Debug bot shutting down...")
        print(f"\n🛑 调试结束 - 共处理 {bot.message_count} 条消息")
    except Exception as e:
        logger.error(f"Debug bot failed: {e}")
        print(f"❌ 调试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 