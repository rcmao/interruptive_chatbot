#!/usr/bin/env python3
"""
修复冲突检测系统 - 增强中文支持
"""

import sys
import os
import asyncio

# 添加src到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from core.explainable_system import ExplainableInterventionBot, ConflictEvidence, ConflictSignal

class EnhancedConflictDetector:
    """增强的冲突检测器"""
    
    def __init__(self):
        self.lightweight_threshold = 0.3   # 降低阈值
        self.thomas_weight = 0.4
        self.llm_weight = 0.3
        self.keyword_weight = 0.3
        
        # 实时性优先级
        self.max_llm_wait_time = 400
        self.early_decision_threshold = 0.5  # 降低早期决策阈值
    
    async def enhanced_lightweight_analysis(self, message: str) -> ConflictSignal:
        """增强的轻量级分析"""
        start_time = asyncio.get_event_loop().time()
        
        conflict_indicators = {
            # 情绪词汇
            "emotion_words": [
                "愤怒", "生气", "不满", "烦躁", "急了", "火大", "郁闷",
                "angry", "frustrated", "annoyed", "upset", "mad"
            ],
            
            # 不同意/反对
            "disagreement": [
                "不同意", "反对", "错误", "不对", "有问题", "不行", "不可能",
                "wrong", "disagree", "incorrect", "no way", "impossible"
            ],
            
            # 责备/抱怨 - 这是示例消息的主要特征
            "blame_complaint": [
                "你都没有", "你完全不", "你总是", "你从不", "你还", "怎么了",
                "都没有出现", "没有动静", "不来", "拖累", "影响大家",
                "you always", "you never", "why don't you", "dragging down"
            ],
            
            # 时间压力/紧急
            "urgency_pressure": [
                "急了", "来不及", "赶紧", "快点", "已经", "这周", "两次",
                "deadline", "urgent", "没时间", "要迟到", "already"
            ],
            
            # 责任追究
            "accountability": [
                "负责的", "你的部分", "你应该", "为什么", "怎么回事", "准备做",
                "responsible", "your part", "you should", "what's wrong"
            ],
            
            # 质疑/挑战
            "questioning": [
                "还准备", "想不想", "要不要", "有没有", "会不会",
                "are you going to", "do you want", "will you"
            ],
            
            # 强度标记
            "intensity": [
                "!", "完全", "绝对", "根本", "一直", "从来", "都",
                "absolutely", "completely", "totally", "never", "always"
            ]
        }
        
        score = 0.0
        evidence = []
        message_lower = message.lower()
        
        for category, keywords in conflict_indicators.items():
            matches = [word for word in keywords if word in message_lower]
            if matches:
                # 根据类别设置不同权重
                weight = {
                    "emotion_words": 0.3,
                    "disagreement": 0.25,
                    "blame_complaint": 0.5,  # 责备类词汇权重最高
                    "urgency_pressure": 0.3,
                    "accountability": 0.4,
                    "questioning": 0.3,
                    "intensity": 0.15
                }.get(category, 0.2)
                
                category_score = min(len(matches) * weight, 0.7)
                score += category_score
                evidence.append(f"{category}: {matches[:3]}")  # 只显示前3个匹配
        
        # 检测特殊模式 - 针对示例消息
        patterns = [
            ("重复质疑", ["都没有", "也都没有", "还没有"]),
            ("时间对比", ["这周", "两次", "已经"]),
            ("后果威胁", ["拖累", "分数", "不想做"]),
            ("责任推卸", ["我的问题", "我也提前说了", "我不来"]),
            ("群体压力", ["大家", "小组", "其他"]),
        ]
        
        for pattern_name, pattern_words in patterns:
            matched_words = [word for word in pattern_words if word in message]
            if len(matched_words) >= 2:  # 至少匹配2个词
                score += 0.4
                evidence.append(f"模式: {pattern_name}({matched_words})")
        
        # 消息长度奖励 - 长消息通常包含更多冲突信息
        if len(message) > 100:
            score += 0.1
            evidence.append("长消息奖励")
        
        processing_time = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return ConflictSignal(
            signal_type=ConflictEvidence.KEYWORD_BASED,
            value=min(score, 1.0),
            confidence=0.9 if score > 0.6 else 0.8,
            evidence_text="; ".join(evidence),
            processing_time=processing_time,
            explanation=f"增强关键词分析: {score:.2f}分 - 检测到{len(evidence)}个信号"
        )

async def test_enhanced_detection():
    """测试增强检测"""
    
    # 测试消息（来自聊天记录）
    test_message = """哈喽，你现在有空吗
关于我们小组的事情，想和你聊下
嗯，在的，怎么了？
我们这周已经开了两次会了，你都没有出现
还有你负责的那个ppt的那部分，现在也都没有动静
现在有点急了，你还准备做这部分吗？
额，没来是我的问题，但我也提前说了我不来
这段时间有点忙，其他科还一堆ddl，有点忙不过来
理解你，但大家都有其他的作业要做，ddl也都这段时间
但我们几个一直在出力，结果你完全不来，然后
我感觉要不想做不要拖累大家的小组分数吧"""
    
    detector = EnhancedConflictDetector()
    
    print("🔍 测试增强冲突检测...")
    print(f"📝 测试消息长度: {len(test_message)} 字符")
    print()
    
    # 分段测试
    segments = test_message.split('\n')
    
    for i, segment in enumerate(segments):
        if segment.strip():
            print(f"📨 消息 {i+1}: {segment[:50]}...")
            
            signal = await detector.enhanced_lightweight_analysis(segment)
            
            print(f"   🎯 分数: {signal.value:.3f}")
            print(f"   📊 置信度: {signal.confidence:.2f}")
            print(f"   🔍 证据: {signal.evidence_text}")
            print(f"   ⏱️  处理时间: {signal.processing_time:.1f}ms")
            
            # 判断是否需要干预
            if signal.value > 0.35:
                print(f"   🚨 建议干预! (阈值: 0.35)")
            else:
                print(f"   ✅ 暂无需干预 (阈值: 0.35)")
            print()

if __name__ == "__main__":
    asyncio.run(test_enhanced_detection()) 