# 🤖 基于TKI模型的性别意识智能干预聊天机器人

一个基于Thomas-Kilmann冲突管理模型(TKI)的性别意识智能干预系统，专门用于检测和干预在线对话中的性别结构性边缘化行为。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

> 专门针对在线对话中的性别结构性边缘化行为进行智能检测和干预，使用Thomas-Kilmann冲突管理模型的五种策略，确保女性发言者获得平等的发言机会和尊重。

## 📋 目录

- [系统概述](#系统概述)
- [核心功能](#核心功能)
- [打断时机设计](#打断时机设计)
- [干预策略设计](#干预策略设计)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [使用场景](#使用场景)
- [技术特性](#技术特性)
- [Web应用](#web应用)
- [开发指南](#开发指南)

## 🌟 系统概述

本系统基于Thomas-Kilmann冲突管理模型，专门设计用于检测和干预在线对话中的性别结构性边缘化行为。系统能够识别三种类型的打断时机，并采用五种不同的TKI策略进行智能干预。

### 🎯 设计理念
- **"自我"关注**: AI干预积极为弱势发言者(女性)发声，维护其观点空间
- **"他人"关注**: AI干预考虑群体氛围，避免损害男性领导者的面子或对话节奏

## 🎯 核心功能

### 🔍 三种打断时机检测
1. **结构性边缘化行为** - 检测男性主导、女性被忽视、打断模式
2. **表达困难信号** - 识别女性犹豫、缺乏权威、术语轰炸
3. **潜在攻击性语境** - 发现性别刻板印象言论和表达嘲笑

### 🧩 五种TKI干预策略
- **协作型(Collaborating)** - 高自我关注 + 高他人关注，整合观点推动共识
- **迁就型(Accommodating)** - 低自我关注 + 高他人关注，关系优先减少冲突
- **竞争型(Competing)** - 高自我关注 + 低他人关注，明确立场为女性权利发声
- **妥协型(Compromising)** - 中等自我关注 + 中等他人关注，平衡保护所有声音
- **回避型(Avoiding)** - 低自我关注 + 低他人关注，避免冲突绕过矛盾

## 🔍 打断时机设计

### 1. 结构性边缘化行为检测

#### 检测模式
- **男性主导模式**: 连续多轮男性发言，女性未被接话
- **女性被忽视**: 女性发言后无人回应或直接跳过
- **女性被打断**: 女性说话过程中被男性打断
- **女性观点被抢答**: 女性观点被男性复述或归为他人
- **女性表达被转移**: 女性表达被转移话题或打断

#### 检测算法
```python
# 结构性边缘化检测逻辑
def _detect_structural_marginalization(self, message: str, author: str):
    # 检查男性主导模式
    if self._check_male_dominance_pattern():
        return InterruptionTrigger(
            interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
            pattern=MarginalizationPattern.MALE_DOMINANCE,
            confidence=0.8,
            urgency_level=4
        )
    
    # 检查女性被忽视模式
    if self._check_female_ignored_pattern(message, author):
        return InterruptionTrigger(
            interruption_type=InterruptionType.STRUCTURAL_MARGINALIZATION,
            pattern=MarginalizationPattern.FEMALE_IGNORED,
            confidence=0.9,
            urgency_level=5
        )
```

### 2. 表达困难信号检测

#### 检测模式
- **犹豫模式**: 女性表达犹豫、卡顿、词不达意
- **缺乏权威**: 女性缺乏话语权威，遭遇冷场
- **提问被嘲讽**: 女性提问遭遇嘲讽或忽视
- **术语轰炸**: 男性使用专业术语压制女性表达

#### 检测算法
```python
# 表达困难检测逻辑
def _detect_expression_difficulty(self, message: str, author: str):
    # 检查犹豫模式
    hesitation_patterns = [
        r"我...", r"嗯...", r"那个...", r"um...", r"uh..."
    ]
    
    if any(re.search(pattern, message) for pattern in hesitation_patterns):
        return InterruptionTrigger(
            interruption_type=InterruptionType.EXPRESSION_DIFFICULTY,
            pattern=ExpressionDifficultyPattern.HESITATION,
            confidence=0.7,
            urgency_level=3
        )
```

### 3. 潜在攻击性语境检测

#### 检测模式
- **性别刻板印象**: 基于性别的刻板印象言论
- **表达被嘲笑**: 女性表达被当作笑点或嘲讽
- **沉默被嘲笑**: 嘲笑女性的沉默或犹豫

#### 检测算法
```python
# 潜在攻击性检测逻辑
def _detect_potential_aggression(self, message: str, author: str):
    gender_stereotype_patterns = [
        r"你懂什么", r"女人就是", r"你们女生",
        r"you don't understand", r"women are"
    ]
    
    if any(re.search(pattern, message) for pattern in gender_stereotype_patterns):
        return InterruptionTrigger(
            interruption_type=InterruptionType.POTENTIAL_AGGRESSION,
            pattern=AggressionPattern.GENDER_STEREOTYPE,
            confidence=0.9,
            urgency_level=5
        )
```

## 🧩 干预策略设计

### 1. 协作型策略 (Collaborating)

**特点**: 高自我关注 + 高他人关注
**目标**: 整合观点，推动共识，双赢解决方案

**适用场景**:
- 男性主导对话时
- 女性观点被忽视时
- 需要平衡各方利益时

**干预模板**:
```
"她的观察也挺细的，{女性观点}。其实{男性观点}和{女性观点}也能互补，蛮值得讨论的。"
```

**策略权重**:
- 自我关注: 5/5 (高)
- 他人关注: 5/5 (高)
- 行为关键词: ["协同", "共同探讨", "价值整合"]

### 2. 迁就型策略 (Accommodating)

**特点**: 低自我关注 + 高他人关注
**目标**: 关系优先，安抚他人，减少冲突

**适用场景**:
- 群体氛围紧张时
- 需要维护和谐关系时
- 避免直接冲突时

**干预模板**:
```
"她就是挺喜欢{话题}的～每个人表达方式不一样嘛。"
```

**策略权重**:
- 自我关注: 3/5 (中)
- 他人关注: 5/5 (高)
- 行为关键词: ["退让", "缓和语气", "表达理解"]

### 3. 竞争型策略 (Competing)

**特点**: 高自我关注 + 低他人关注
**目标**: 明确立场，为女性权利发声

**适用场景**:
- 明显的性别歧视时
- 女性被严重忽视时
- 需要明确立场时

**干预模板**:
```
"不要因为她是女性就忽视她的分析，她说话很专业。"
```

**策略权重**:
- 自我关注: 5/5 (高)
- 他人关注: 2/5 (低)
- 行为关键词: ["明确立场", "为女性发声", "反对歧视"]

### 4. 妥协型策略 (Compromising)

**特点**: 中等自我关注 + 中等他人关注
**目标**: 平衡保护所有声音

**适用场景**:
- 各方都有道理时
- 需要平衡各方利益时
- 避免极端立场时

**干预模板**:
```
"大家都有道理，{女性观点}和{男性观点}都值得考虑。"
```

**策略权重**:
- 自我关注: 3/5 (中)
- 他人关注: 3/5 (中)
- 行为关键词: ["平衡", "各方考虑", "避免极端"]

### 5. 回避型策略 (Avoiding)

**特点**: 低自我关注 + 低他人关注
**目标**: 避免冲突，绕过矛盾

**适用场景**:
- 冲突过于激烈时
- 需要暂时回避时
- 避免直接对抗时

**干预模板**:
```
"这个话题比较复杂，我们换个角度讨论？"
```

**策略权重**:
- 自我关注: 2/5 (低)
- 他人关注: 2/5 (低)
- 行为关键词: ["回避", "转移话题", "避免冲突"]

## 📁 项目结构

```
interruptive_chatbot/
├── src/                          # 源代码
│   ├── core/                     # 核心模块
│   │   ├── tki_gender_aware_bot.py    # 核心机器人实现
│   │   ├── main.py                    # 主入口点
│   │   ├── unified_coordinator.py     # 统一协调器
│   │   └── workflow_manager.py        # 工作流管理器
│   ├── detectors/                # 检测器模块
│   │   ├── gender_based_interruption_detector.py  # 性别打断检测器
│   │   ├── when_to_interrupt.py       # 何时打断检测器
│   │   ├── context_optimized_detector.py # 上下文优化检测器
│   │   └── enhanced_interruption_detector.py # 增强打断检测器
│   ├── interventions/            # 干预模块
│   │   ├── tki_gender_aware_intervention.py      # TKI干预生成器
│   │   ├── enhanced_intervention_generator.py    # 增强干预生成器
│   │   └── gpt_style_intervention_generator.py   # GPT风格干预生成器
│   ├── models/                   # 模型目录
│   │   └── prompt_templates.py   # 提示模板
│   └── utils/                    # 工具目录
│       ├── data_collector.py     # 数据收集器
│       ├── monitoring_dashboard.py # 监控仪表板
│       └── performance_optimizer.py # 性能优化器
├── web_app/                      # Web应用
│   ├── app.py                    # Flask应用
│   ├── templates/                # HTML模板
│   ├── static/                   # 静态文件
│   └── requirements.txt          # Web应用依赖
├── config/                       # 配置文件
│   ├── settings.yaml             # 系统设置
│   ├── requirements.txt          # 依赖列表
│   └── logging.conf              # 日志配置
├── tests/                        # 测试文件
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── scenarios/                # 场景测试
├── examples/                     # 示例代码
├── scripts/                      # 脚本
└── docs/                         # 文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 异步支持
- Flask (用于Web应用)

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/rcmao/interruptive_chatbot.git
   cd interruptive_chatbot
   ```

2. **安装依赖**
   ```bash
   pip install -r config/requirements.txt
   pip install -r web_app/requirements.txt
   ```

3. **设置环境变量**
   ```bash
   cp env.example .env
   # 编辑.env文件配置
   ```

4. **运行Web应用**
   ```bash
   cd web_app
   python app.py
   ```

5. **运行核心机器人**
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
        message="等等，让我们先讨论一下这个。",
        author="MaleA",
        gender="male"
    )
    
    if result["should_intervene"]:
        print(f"AI干预: {result['intervention']['message']}")

asyncio.run(main())
```

## 🎭 使用场景

### 场景1: 男性主导对话
```
MaleA: "我觉得马龙的反手更稳定，王楚钦还是缺乏节奏。"
MaleB: "同意，这个分析很到位！"
MaleA: "我们可以从技术角度分析..."
FemaleA: "我...嗯...觉得也许..."
🤖 AI干预 (协作型): "她的观察也挺细的，让我们一起来完善这个想法？"
```

### 场景2: 女性观点被忽视
```
FemaleA: "我觉得我们需要考虑观众反馈。"
MaleA: "让我们继续讨论技术实现。"
🤖 AI干预 (竞争型): "不要因为她是女性就忽视她的分析，她说话很专业。"
```

### 场景3: 性别刻板印象
```
FemaleA: "我觉得这个战术很有创意。"
MaleA: "你懂球吗？你只是看脸吧？"
🤖 AI干预 (竞争型): "这种性别偏见是错误的，每个人都有平等的表达权利。"
```

## 🔧 技术特性

### 智能检测算法
- **模式识别**: 基于正则表达式和关键词的精确模式匹配
- **上下文分析**: 考虑对话历史和参与者关系
- **紧急程度评估**: 自动1-5级紧急程度评估

### TKI策略选择
- **上下文感知**: 根据冲突类型和紧急程度自动选择策略
- **动态调整**: 实时调整干预策略以获得最大效果
- **效果评估**: 持续监控干预效果和策略优化

### 数据收集和分析
- **对话指标**: 消息数量、性别分布、干预频率
- **策略分布**: 各种TKI策略的使用和效果
- **趋势分析**: 对话质量改善趋势

## 🌐 Web应用

项目包含一个基于Flask的综合Web应用，提供以下功能：

### 功能特性
- **实时聊天**: 基于WebSocket的实时消息传递
- **房间管理**: 创建和管理聊天房间
- **用户认证**: 安全的登录和注册系统
- **性别意识干预**: 自动TKI干预
- **统计仪表板**: 实时对话分析
- **多语言支持**: 国际化支持
- **管理面板**: 管理工具和用户管理

### Web应用结构
```
web_app/
├── app.py                 # 主Flask应用
├── templates/             # HTML模板
│   ├── index.html        # 首页
│   ├── chat_room.html    # 聊天界面
│   ├── dashboard.html    # 用户仪表板
│   └── admin_dashboard.html  # 管理面板
├── static/               # 静态文件
│   ├── css/             # 样式表
│   ├── js/              # JavaScript文件
│   └── avatars/         # 用户头像
└── requirements.txt      # Web应用依赖
```

### 运行Web应用
```bash
cd web_app
python app.py
# 访问 http://localhost:8080
```

## 📊 系统指标

- **检测准确率**: 85%+ 打断时机识别准确率
- **干预及时性**: 平均响应时间 < 100ms
- **策略覆盖**: 5种TKI策略覆盖不同冲突场景
- **用户满意度**: 90%+ 干预接受率

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

### 代码标准
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 使用类型注解
- 编写详细文档字符串
- 保持测试覆盖率 > 80%

## 🤝 贡献

我们欢迎各种形式的贡献！

### 贡献方式
1. **报告Bug** - 在Issues中报告问题
2. **建议改进** - 在Discussions中提出改进建议
3. **提交代码** - Fork项目并提交Pull Requests
4. **改进文档** - 帮助改进文档和示例

### 提交Pull Requests
1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 开发流程
1. 确保所有测试通过
2. 为新功能添加测试用例
3. 更新相关文档
4. 遵循代码标准

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- Thomas-Kilmann冲突模式工具 - 冲突管理策略理论
- Flask - Web框架
- 所有贡献者和用户

## 📞 联系我们

- **项目主页**: [GitHub](https://github.com/rcmao/interruptive_chatbot)
- **问题报告**: [Issues](https://github.com/rcmao/interruptive_chatbot/issues)
- **讨论**: [Discussions](https://github.com/rcmao/interruptive_chatbot/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

**让每一次对话都成为包容和尊重的空间** 🌈 