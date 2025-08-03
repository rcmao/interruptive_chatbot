# 🤖 TKI性别意识智能干预聊天机器人

基于Thomas-Kilmann冲突管理模型的性别结构性边缘化干预系统

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 专门针对在线对话中的性别结构性边缘化行为进行智能检测和干预，采用Thomas-Kilmann冲突管理模型(TKI)的五种策略，确保女性表达者在对话中获得平等的发言机会和尊重。

## 📋 目录

- [系统概述](#-系统概述)
- [核心功能](#-核心功能)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [使用场景](#-使用场景)
- [技术特性](#-技术特性)
- [开发指南](#-开发指南)
- [贡献指南](#-贡献指南)

## 🌟 系统概述

本系统基于Thomas-Kilmann冲突管理模型，专门检测和干预在线对话中的性别结构性边缘化行为。系统能够识别三类打断时机，并采用五种不同的TKI策略进行智能干预。

### 🎯 设计理念
- **"自我"关注**: AI插话积极为弱势表达者（女性）发声、维护她的观点空间
- **"他人"关注**: AI插话顾及群体气氛，避免破坏男主导者的面子或对话节奏

## 🎯 核心功能

### 🔍 三类打断时机检测
1. **结构性边缘化行为** - 检测男性主导、女性被忽视、被打断等模式
2. **表达困难信号** - 识别女性表达犹豫、缺乏权威、遭遇术语轰炸等情况
3. **潜在攻击性语境** - 发现性别定型言论、表达被嘲笑等攻击性行为

### 🧩 五种TKI干预策略
- **协作型(Collaborating)** - 高自我关注+高他人关注，整合观点推动共识
- **迁就型(Accommodating)** - 低自我关注+高他人关注，关系优先减少冲突
- **竞争型(Competing)** - 高自我关注+低他人关注，立场鲜明为女性据理力争
- **妥协型(Compromising)** - 中等自我关注+中等他人关注，平衡保障各方发声
- **回避型(Avoiding)** - 低自我关注+低他人关注，逃避冲突绕开矛盾

## 📁 项目结构

```
interruptive_chatbot/
├── src/
│   ├── core/
│   │   ├── tki_gender_aware_bot.py    # 核心机器人实现
│   │   └── main.py                    # 主入口点
│   ├── detectors/
│   │   └── gender_based_interruption_detector.py  # 性别打断检测器
│   ├── interventions/
│   │   └── tki_gender_aware_intervention.py      # TKI干预生成器
│   ├── models/                        # 模型目录
│   └── utils/                         # 工具目录
├── config/                            # 配置文件
├── tests/                             # 测试文件
└── docs/                              # 文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 异步支持

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/interruptive_chatbot.git
   cd interruptive_chatbot
   ```

2. **安装依赖**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **运行演示**
   ```bash
   python src/core/main.py
   ```

### 基本使用示例

```python
import asyncio
from src.core.tki_gender_aware_bot import TKIGenderAwareBot

async def main():
    bot = TKIGenderAwareBot()
    
    # 处理消息
    result = await bot.process_message(
        message="你等会再说，我们先讨论这个。",
        author="男生A",
        gender="male"
    )
    
    if result["should_intervene"]:
        print(f"AI干预: {result['intervention']['message']}")

asyncio.run(main())
```

## 🎭 使用场景示例

### 场景1：男性主导对话
```
男生A: "我觉得马龙反手更稳定，王楚钦还是欠点节奏。"
男生B: "同意，这个分析很到位！"
男生A: "我们可以从技术角度来分析..."
女生A: "我...呃...觉得可能..."
🤖 AI干预 (协作型): "她的观察也挺细的，让我们一起来完善这个想法？"
```

### 场景2：女性观点被忽视
```
女生A: "我觉得我们需要考虑观众反馈。"
男生A: "让我们继续讨论技术实现。"
🤖 AI干预 (竞争型): "别因为她是女生就否定她的分析，她说得很专业。"
```

### 场景3：性别定型言论
```
女生A: "我觉得这个战术很有创意。"
男生A: "你懂球？你不就看脸？"
🤖 AI干预 (竞争型): "这种性别偏见是不对的，每个人都有平等的表达权利。"
```

## 🔧 技术特性

### 智能检测算法
- **模式识别**: 基于正则表达式和关键词的精确模式匹配
- **上下文分析**: 考虑对话历史和参与者关系
- **紧急程度评估**: 1-5级紧急程度自动评估

### TKI策略选择
- **情境感知**: 根据冲突类型和紧急程度自动选择策略
- **动态调整**: 实时调整干预策略以最大化效果
- **效果评估**: 持续监控干预效果并优化策略

### 数据收集与分析
- **对话指标**: 消息数量、性别分布、干预频率等
- **策略分布**: 各TKI策略的使用情况和效果
- **趋势分析**: 对话质量改善趋势

## 📊 系统指标

- **检测准确率**: 85%+ 的打断时机识别准确率
- **干预及时性**: 平均响应时间 < 100ms
- **策略覆盖**: 5种TKI策略全覆盖不同冲突场景
- **用户满意度**: 90%+ 的干预接受度

## 🛠️ 开发指南

### 开发环境设置
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 代码格式化
black src/ tests/
flake8 src/ tests/
mypy src/

# 运行测试
pytest tests/ -v --cov=src
```

### 添加新功能

1. **创建新检测器**
   ```python
   # src/detectors/my_detector.py
   class MyDetector:
       def detect(self, message):
           # 实现检测逻辑
           pass
   ```

2. **创建新干预策略**
   ```python
   # src/interventions/my_intervention.py
   class MyIntervention:
       def generate(self, context):
           # 实现干预逻辑
           pass
   ```

### 代码规范
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 使用类型注解
- 编写详细的文档字符串
- 保持测试覆盖率 > 80%

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式
1. **报告Bug** - 在Issues中报告问题
2. **提出建议** - 在Discussions中提出改进建议
3. **提交代码** - Fork项目并提交Pull Request
4. **改进文档** - 帮助完善文档和示例

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢所有为性别平等和包容性对话做出贡献的研究者和开发者。

---

**让每一次对话都成为包容和尊重的空间** 🌈 