"""
最终版本的系统测试
"""

import asyncio
import os
from datetime import datetime

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "sk-XGGe5y0ZvLcQVFp6XnRizs7q47gsVnAbZx0Xr2mfcVlbr99f"
os.environ["OPENAI_API_BASE"] = "https://api2.aigcbest.top/v1"

from main import MessageData
from optimized_monitoring_fixed import OptimizedConflictMonitorFixed

async def test_real_system():
    """测试真实系统"""
    print("🧪 最终系统测试")
    print("=" * 50)
    
    # 初始化监控器
    monitor = OptimizedConflictMonitorFixed(
        os.environ["OPENAI_API_KEY"],
        os.environ["OPENAI_API_BASE"]
    )
    
    await monitor.initialize()
    
    # 测试场景
    test_scenarios = [
        "这个方案很不错",                    # 中性 - 预期不干预
        "我不太同意这个想法",                # 轻微分歧 - 预期不干预
        "这个设计完全不合理！",              # 强烈反对 - 预期可能干预
        "你从不考虑别人的想法",              # 人身攻击 - 预期干预
        "你错了，这样绝对不行！",            # 激烈冲突 - 预期干预
        "算了，我不想争论了"                 # 放弃 - 预期不干预
    ]
    
    interventions = []
    
    for i, content in enumerate(test_scenarios, 1):
        print(f"\n📝 测试场景 {i}: {content}")
        
        message = MessageData(
            author_id=i % 2 + 1,  # 交替用户
            author_name=f"用户{i % 2 + 1}",
            content=content,
            timestamp=datetime.now(),
            typing_duration=2.0,
            edits_count=0,
            reactions=[]
        )
        
        try:
            should_intervene, score, reason, signals = await monitor.process_message(message)
            
            print(f"   分数: {score:.2f}")
            print(f"   干预: {'是' if should_intervene else '否'}")
            print(f"   原因: {reason}")
            
            if should_intervene:
                interventions.append({
                    "scene": i,
                    "content": content,
                    "score": score,
                    "reason": reason
                })
            
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
    
    # 结果分析
    print(f"\n📊 测试结果分析:")
    print(f"总场景数: {len(test_scenarios)}")
    print(f"触发干预: {len(interventions)}")
    print(f"干预率: {len(interventions)/len(test_scenarios)*100:.1f}%")
    
    if interventions:
        print(f"\n🚨 干预详情:")
        for intervention in interventions:
            print(f"  场景{intervention['scene']}: {intervention['content'][:20]}... (分数:{intervention['score']:.2f})")
    
    # 性能指标
    metrics = monitor.get_performance_metrics()
    print(f"\n⚡ 性能指标:")
    print(f"平均响应时间: {metrics.get('avg_response_time', 0):.3f}s")
    print(f"处理的信号数: {metrics.get('total_signals_processed', 0)}")
    
    return len(interventions) > 0

if __name__ == "__main__":
    result = asyncio.run(test_real_system())
    if result:
        print("\n🎉 系统测试通过！检测到冲突并能够干预。")
    else:
        print("\n⚠️  系统过于保守，建议进一步调整阈值。") 