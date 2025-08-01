"""
实时监控仪表板
显示每句话的分析结果和上下文状态
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List
import logging

class ConflictMonitor:
    """冲突监控器"""
    
    def __init__(self):
        self.is_monitoring = False
        self.log_file = "logs/conflict_analysis.log"
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ConflictMonitor')
    
    def log_analysis(self, analysis_record: Dict):
        """记录分析结果"""
        
        # 格式化输出
        timestamp = analysis_record['timestamp'].strftime('%H:%M:%S')
        author = analysis_record['author']
        message = analysis_record['message']
        
        # 分数显示
        single_score = analysis_record['single_score']
        context_score = analysis_record['context_score'] 
        urgency = analysis_record['urgency']
        level = analysis_record['escalation_level']
        pattern = analysis_record['pattern'] or '无'
        
        # 状态指示器
        status_icon = "🚨" if analysis_record['should_intervene'] else "✅"
        
        # 分数条形图
        def score_bar(score, width=10):
            filled = int(score * width)
            return "█" * filled + "░" * (width - filled)
        
        # 输出格式
        log_message = f"""
{status_icon} [{timestamp}] {author}
📝 {message}
📊 单句:{single_score:.2f} {score_bar(single_score)} | 上下文:{context_score:.2f} {score_bar(context_score)} | 紧急度:{urgency:.2f} {score_bar(urgency)}
🎯 等级:{level}/5 | 模式:{pattern}
        """.strip()
        
        self.logger.info(log_message)
        
        # 如果需要干预，高亮显示
        if analysis_record['should_intervene']:
            self.logger.warning(f"🚨 干预建议: {analysis_record.get('intervention', '无')}")
    
    def print_dashboard_header(self):
        """打印仪表板头部"""
        header = """
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                            🤖 智能冲突检测监控仪表板                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║ 图例: 🚨=需要干预 ✅=正常 📊=分数条形图 🎯=升级等级 📝=消息内容                             ║
║ 分数范围: 0.0-1.0 | 等级范围: 1-5 | 模式: escalating/repeating/deadline等              ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
        """
        print(header)
    
    def start_monitoring(self):
        """开始监控"""
        self.is_monitoring = True
        self.print_dashboard_header()
        self.logger.info("🔥 开始实时冲突检测监控...")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.logger.info("⏹️ 停止冲突检测监控")

# 集成到主bot中
class MonitoredConflictBot:
    """带监控的冲突检测机器人"""
    
    def __init__(self):
        from src.core.context_aware_detector import ContextAwareBot
        self.context_bot = ContextAwareBot()
        self.monitor = ConflictMonitor()
        self.monitor.start_monitoring()
    
    async def process_message(self, message: str, author: str, channel_id: str) -> str:
        """处理消息并显示监控信息"""
        
        # 分析消息
        result = await self.context_bot.analyze_message_with_context(message, author)
        
        # 记录到监控
        self.monitor.log_analysis(result['analysis_record'])
        
        # 返回干预消息
        if result['should_intervene']:
            return result['intervention_message']
        
        return None
    
    def get_dashboard_summary(self) -> str:
        """获取仪表板摘要"""
        dashboard = self.context_bot.get_monitoring_dashboard()
        
        if dashboard.get('status') == '暂无数据':
            return "📊 暂无分析数据"
        
        stats = dashboard['statistics']
        current = dashboard['current_status']
        
        summary = f"""
📊 实时监控摘要
├─ 对话时长: {current['conversation_duration']}
├─ 参与人数: {current['active_participants']}
├─ 总消息数: {stats['total_messages']}
├─ 干预次数: {stats['interventions']}
├─ 平均紧急度: {stats['avg_urgency']:.2f}
├─ 最高等级: {stats['max_escalation']}/5
└─ 当前趋势: {current['trend']}
        """.strip()
        
        return summary

# 测试脚本
async def test_monitoring():
    """测试监控功能"""
    
    bot = MonitoredConflictBot()
    
    # 测试对话
    test_conversation = [
        ("Alice", "大家好，我们讨论一下项目进度吧"),
        ("Bob", "好的，我这边基本完成了"),
        ("Alice", "那个报告你写了吗？明天就要交了"),
        ("Bob", "啊...我忘记了，现在开始写来得及吗？"),
        ("Alice", "什么？你怎么能忘记！我们都说了好几次了"),
        ("Bob", "对不起，最近确实很忙..."),
        ("Alice", "忙？我们大家都很忙！你这样会影响整个团队的！"),
        ("Bob", "我知道错了，我现在就去写"),
        ("Alice", "现在写？你觉得一晚上能写完？我们组的分数就被你拖累了！")
    ]
    
    print("开始监控测试...")
    
    for author, message in test_conversation:
        intervention = await bot.process_message(message, author, "test_channel")
        
        if intervention:
            print(f"💬 机器人干预: {intervention}")
        
        # 短暂延迟模拟真实对话
        await asyncio.sleep(0.5)
    
    # 显示最终摘要
    print("\n" + "="*50)
    print(bot.get_dashboard_summary())

if __name__ == "__main__":
    asyncio.run(test_monitoring()) 