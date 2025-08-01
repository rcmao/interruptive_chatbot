"""
简化的测试脚本，用于快速验证系统功能
"""

import asyncio
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# 模拟环境变量
os.environ['DISCORD_TOKEN'] = 'test_token'
os.environ['OPENAI_API_KEY'] = 'test_api_key'
os.environ['OPENAI_API_BASE'] = 'http://test.api.base'

def test_basic_imports():
    """测试基本模块导入"""
    try:
        from main import (
            MessageData, ConflictSignal, TKIStrategy, ConflictPhase,
            MultiSignalConflictMonitor, InterventionTriggerLogic,
            TKIStrategySelector, SlotBasedPromptGenerator,
            RealTimeInteractionModule
        )
        print("✅ 基本模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_data_structures():
    """测试数据结构"""
    try:
        from main import MessageData, ConflictSignal, TKIStrategy
        
        # 测试 MessageData
        message = MessageData(
            author_id=1,
            author_name="TestUser",
            content="测试消息",
            timestamp=datetime.now()
        )
        assert message.author_id == 1
        assert message.content == "测试消息"
        
        # 测试 ConflictSignal
        signal = ConflictSignal(
            llm_score=0.7,
            turn_taking_issues=["dominance"],
            typing_behavior={"frustration": 0.8},
            emotion_phrases=["你错了"],
            timestamp=datetime.now()
        )
        assert signal.llm_score == 0.7
        
        # 测试 TKIStrategy
        assert TKIStrategy.COLLABORATING.value == "collaborating"
        
        print("✅ 数据结构测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据结构测试失败: {e}")
        return False

def test_lightweight_detector():
    """测试轻量级检测器"""
    try:
        from optimized_monitoring import LightweightConflictDetector
        
        detector = LightweightConflictDetector()
        
        # 测试高冲突内容
        high_conflict = "你总是这样，太荒谬了！"
        score = detector.quick_score(high_conflict, [])
        assert score > 0.3, f"高冲突内容应该有较高分数，实际: {score}"
        
        # 测试中性内容
        neutral = "我认为我们可以讨论一下这个方案"
        score = detector.quick_score(neutral, [])
        assert score < 0.3, f"中性内容应该有低分数，实际: {score}"
        
        print("✅ 轻量级检测器测试通过")
        return True
    except Exception as e:
        print(f"❌ 轻量级检测器测试失败: {e}")
        return False

def test_prompt_templates():
    """测试提示模板"""
    try:
        from prompt_templates import PromptTemplateLibrary, TKIStrategy
        
        library = PromptTemplateLibrary()
        
        # 测试模板获取
        templates = library.get_templates_for_strategy(TKIStrategy.COLLABORATING)
        assert len(templates) > 0, "协作策略应该有模板"
        
        # 测试随机模板
        template = library.get_random_template(TKIStrategy.ACCOMMODATING)
        assert template is not None, "应该能获取到随机模板"
        
        print("✅ 提示模板测试通过")
        return True
    except Exception as e:
        print(f"❌ 提示模板测试失败: {e}")
        return False

async def test_mock_integration():
    """测试模拟集成"""
    try:
        from main import RealTimeInteractionModule
        
        # 创建模拟模块
        module = RealTimeInteractionModule("test_key", "http://test.api")
        
        # 模拟Discord消息
        mock_message = Mock()
        mock_message.author.id = 1
        mock_message.author.display_name = "TestUser"
        mock_message.content = "这个想法太荒谬了！"
        mock_message.created_at = datetime.now()
        
        # 模拟LLM响应
        with patch.object(module.monitor, 'compute_llm_conflict_score') as mock_llm:
            mock_llm.return_value = 0.8
            
            result = await module.process_message(mock_message)
            
            # 验证处理结果
            assert isinstance(result, (str, type(None))), "应该返回字符串或None"
        
        print("✅ 模拟集成测试通过")
        return True
    except Exception as e:
        print(f"❌ 模拟集成测试失败: {e}")
        return False

async def run_all_tests():
    """运行所有测试"""
    print("🧪 开始简化测试套件")
    print("=" * 40)
    
    tests = [
        ("基本模块导入", test_basic_imports),
        ("数据结构", test_data_structures),
        ("轻量级检测器", test_lightweight_detector),
        ("提示模板", test_prompt_templates),
        ("模拟集成", test_mock_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 运行 {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {test_name} 通过")
                results.append(True)
            else:
                print(f"❌ {test_name} 失败")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            results.append(False)
    
    # 输出结果摘要
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统基本功能正常。")
    else:
        print("⚠️  部分测试失败，请检查问题。")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 