"""
智能冲突干预聊天机器人 - 主入口（带实时监控）
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

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

# 导入正确的模块
from src.core.explainable_system import ExplainableInterventionBot

# 全局监控变量
message_count = 0
intervention_count = 0
start_time = datetime.now()

def format_score_bar(score: float, width: int = 8) -> str:
    """格式化分数条形图"""
    filled = int(score * width)
    return "█" * filled + "░" * (width - filled)

def print_startup_banner():
    """打印启动横幅"""
    banner = f"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                      🤖 智能冲突检测机器人 - 实时监控模式                             ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║ 启动时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}                                                ║
║ 监控状态: ✅ 已启用                                                               ║
║ 日志位置: logs/bot_monitoring.log                                              ║
║                                                                              
"""
    print(banner)

class IntelligentConflictBot:
    """智能冲突干预机器人 - Discord客户端包装器（带监控）"""
    
    def __init__(self):
        self.intervention_bot = ExplainableInterventionBot()
        self.monitor = MonitoringSystem()
        self.discord_client = None
        
    async def start(self, token: str):
        """启动Discord机器人"""
        import discord
        
        # 显示启动横幅
        self.monitor.print_startup_banner()
        
        class DiscordBot(discord.Client):
            def __init__(self, intervention_bot, monitor):
                super().__init__(intents=discord.Intents.default())
                self.intervention_bot = intervention_bot
                self.monitor = monitor
                
            async def on_ready(self):
                logger.info(f'🚀 机器人已登录为 {self.user}')
                print(f"\n🌟 {self.user} 已上线，开始实时监控...")
                print("=" * 70)
                
            async def on_message(self, message):
                # 忽略机器人自己的消息
                if message.author == self.user:
                    return
                
                # 记录处理时间
                start_time = asyncio.get_event_loop().time()
                
                # 捕获日志输出（用于提取分数）
                import io
                import sys
                from contextlib import redirect_stderr, redirect_stdout
                
                log_capture = io.StringIO()
                
                try:
                    # 处理消息
                    intervention = await self.intervention_bot.process_message_with_explanation(
                        message.content, 
                        message.author.display_name, 
                        str(message.channel.id)
                    )
                    
                    processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    # 从日志中提取分数（简化版本）
                    scores = {
                        'final_score': 0.4 if intervention else 0.1,
                        'keyword_score': 0.2,  # 这些需要从实际日志中提取
                        'llm_score': 0.3 if intervention else 0.1
                    }
                    
                    # 记录监控信息
                    self.monitor.log_message_analysis(
                        message.content,
                        message.author.display_name,
                        intervention,
                        processing_time,
                        scores
                    )
                    
                    # 发送干预消息
                    if intervention:
                        await message.channel.send(intervention)
                        
                except Exception as e:
                    processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    logger.error(f"处理消息失败: {e}")
                    
                    # 记录错误
                    self.monitor.log_message_analysis(
                        message.content,
                        message.author.display_name,
                        None,
                        processing_time,
                        {'final_score': 0.0, 'keyword_score': 0.0, 'llm_score': 0.0}
                    )
        
        # 创建并启动Discord客户端
        self.discord_client = DiscordBot(self.intervention_bot, self.monitor)
        await self.discord_client.start(token)

async def main():
    """主函数"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found")
        return
    
    bot = IntelligentConflictBot()
    
    try:
        logger.info("Starting intelligent conflict intervention bot with monitoring...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
        print("\n🛑 机器人已停止监控")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

现在还需要修改 `explainable_system.py` 来更好地暴露分数信息：

```python:src/core/explainable_system_enhanced.py
"""
增强的可解释系统 - 暴露详细分数信息
"""

# 在现有的 ExplainableInterventionBot 类中添加方法

class ExplainableInterventionBot:
    """可解释性冲突干预机器人（增强版）"""
    
    def __init__(self):
        self.analyzer = HybridConflictAnalyzer()
        self.last_analysis = None  # 保存最后一次分析结果
        
    async def process_message_with_explanation(self, message: str, author: str, channel_id: str) -> Optional[str]:
        """处理消息并生成解释（增强版）"""
        
        # 分析冲突
        decision = await self.analyzer.analyze_with_explanation(
            message, 
            {"channel_id": channel_id, "author": author}
        )
        
        # 保存分析结果供监控使用
        self.last_analysis = decision
        
        # 记录详细日志（带分数信息）
        logger.info(f"🔍 冲突分析结果:")
        logger.info(f"   决策: {'干预' if decision.should_intervene else '不干预'}")
        logger.info(f"   置信度: {decision.confidence_level.value}")
        logger.info(f"   Thomas阶段: {decision.thomas_stage}")
        logger.info(f"   处理时间: {sum(decision.processing_breakdown.values()):.1f}ms")
        
        # 详细分数记录
        for signal in decision.evidence_chain:
            logger.info(f"   ✅ {signal.explanation} (分数: {signal.value:.2f})")
        
        for signal in decision.conflicting_signals:
            logger.info(f"   ⚠️ {signal.explanation} (分数: {signal.value:.2f})")
        
        if decision.should_intervene:
            # 生成干预消息
            intervention = self._generate_transparent_intervention(decision)
            return intervention
        
        return None
    
    def get_last_analysis_scores(self) -> dict:
        """获取最后一次分析的详细分数"""
        if not self.last_analysis:
            return {
                'keyword_score': 0.0,
                'thomas_score': 0.0,
                'llm_score': 0.0,
                'final_score': 0.0,
                'confidence': 0.0
            }
        
        # 从evidence_chain中提取各项分数
        scores = {
            'keyword_score': 0.0,
            'thomas_score': 0.0,
            'llm_score': 0.0,
            'final_score': 0.0,
            'confidence': 0.0
        }
        
        for signal in self.last_analysis.evidence_chain:
            if signal.signal_type == ConflictEvidence.KEYWORD_BASED:
                scores['keyword_score'] = signal.value
            elif signal.signal_type == ConflictEvidence.BEHAVIORAL_SIGNAL:
                scores['thomas_score'] = signal.value
            elif signal.signal_type == ConflictEvidence.LLM_SEMANTIC:
                scores['llm_score'] = signal.value
        
        # 计算最终分数
        total_weight = 0.0
        weighted_sum = 0.0
        
        for signal in self.last_analysis.evidence_chain:
            weight = 0.3  # 默认权重
            if signal.signal_type == ConflictEvidence.KEYWORD_BASED:
                weight = 0.4
            elif signal.signal_type == ConflictEvidence.BEHAVIORAL_SIGNAL:
                weight = 0.4
            elif signal.signal_type == ConflictEvidence.LLM_SEMANTIC:
                weight = 0.2
            
            weighted_sum += signal.value * weight * signal.confidence
            total_weight += weight * signal.confidence
        
        scores['final_score'] = weighted_sum / total_weight if total_weight > 0 else 0.0
        scores['confidence'] = sum(s.confidence for s in self.last_analysis.evidence_chain) / len(self.last_analysis.evidence_chain) if self.last_analysis.evidence_chain else 0.0
        
        return scores 