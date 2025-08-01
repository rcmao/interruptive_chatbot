#!/bin/bash

echo "🧪 冲突干预聊天机器人测试套件"
echo "================================"

# 检查依赖
echo "📦 检查测试依赖..."
pip install pytest pytest-asyncio pytest-cov pytest-mock

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 快速测试
echo -e "\n🚀 运行快速测试..."
python test_framework.py quick

# 单元测试
echo -e "\n🔧 运行单元测试..."
pytest test_framework.py::TestLightweightConflictDetector -v
pytest test_framework.py::TestMultiSignalConflictMonitor -v
pytest test_framework.py::TestInterventionTriggerLogic -v
pytest test_framework.py::TestTKIStrategySelector -v
pytest test_framework.py::TestPromptTemplateLibrary -v

# 集成测试
echo -e "\n🔗 运行集成测试..."
pytest test_framework.py::TestSystemIntegration -v

# 性能测试
echo -e "\n⚡ 运行性能测试..."
pytest test_framework.py::TestPerformance -v -m "not slow"

# 端到端测试
echo -e "\n🎯 运行端到端测试..."
pytest test_framework.py::TestEndToEnd -v

# 生成测试报告
echo -e "\n📊 生成测试报告..."
pytest --cov=. --cov-report=html --cov-report=term

echo -e "\n✅ 测试完成！查看 htmlcov/index.html 获取详细覆盖率报告" 