"""
检查Discord机器人权限和连接状态
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def check_bot_permissions():
    """检查机器人权限"""
    try:
        # 创建客户端
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.typing = True
        intents.reactions = True
        
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"✅ 机器人已连接: {client.user}")
            print(f"🆔 机器人ID: {client.user.id}")
            print(f"📝 机器人名称: {client.user.name}")
            
            # 检查机器人权限
            print("\n🔍 检查机器人权限:")
            for guild in client.guilds:
                print(f"服务器: {guild.name}")
                bot_member = guild.get_member(client.user.id)
                if bot_member:
                    permissions = bot_member.guild_permissions
                    print(f"  - 发送消息: {permissions.send_messages}")
                    print(f"  - 读取消息历史: {permissions.read_message_history}")
                    print(f"  - 添加反应: {permissions.add_reactions}")
                    print(f"  - 嵌入链接: {permissions.embed_links}")
                    print(f"  - 使用外部表情: {permissions.use_external_emojis}")
            
            await client.close()
        
        # 连接机器人
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ 未找到DISCORD_TOKEN环境变量")
            return
            
        print(f"🔗 正在连接Discord...")
        await client.start(token)
        
    except discord.LoginFailure:
        print("❌ Discord token无效或已过期")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_bot_permissions()) 