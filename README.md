# 🤖 Interruptive Chatbot - 智能冲突干预聊天机器人

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](https://github.com/yourusername/interruptive_chatbot/actions)

> 基于Thomas冲突模型和TKI策略的智能Discord机器人，能够实时检测对话中的冲突并提供适当的干预，促进健康、建设性的讨论环境。

## 📋 目录

- [功能特点](#-功能特点)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [核心技术](#-核心技术)
- [使用指南](#-使用指南)
- [配置说明](#-配置说明)
- [API文档](#-api文档)
- [开发指南](#-开发指南)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

## ✨ 功能特点

### 🧠 智能检测
- **上下文感知**: 基于对话历史和语境进行冲突检测
- **多模态分析**: 结合文本内容、情感倾向和行为模式
- **实时监控**: <300ms响应时间，确保及时干预
- **自适应学习**: 根据历史数据优化检测准确性

### 🎯 精准干预
- **策略化干预**: 基于TKI理论的五种冲突处理策略
- **个性化响应**: 根据冲突类型和参与者特征调整干预方式
- **可解释决策**: 提供完整的决策解释和证据链
- **渐进式干预**: 从温和提醒到主动调解的多层次干预

### ⚡ 高性能
- **异步处理**: 支持高并发对话处理
- **内存优化**: 高效的数据结构和算法
- **可扩展架构**: 模块化设计，易于扩展和维护
- **监控仪表板**: 实时性能监控和数据分析

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Discord Bot Token
- OpenAI API Key (或其他LLM服务)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/interruptive_chatbot.git
   cd interruptive_chatbot
   ```

2. **自动部署** (推荐)
   ```bash
   ./scripts/deploy.sh
   ```

3. **手动安装**
   ```bash
   # 创建虚拟环境
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或 .venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -r config/requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置你的API密钥
   ```

5. **运行测试**
   ```bash
   ./scripts/run_tests.sh
   ```

6. **启动机器人**
   ```bash
   python src/core/main.py
   # 或使用启动脚本
   ./scripts/start.sh
   ```

### 基本使用示例

```python
from src.core.main import InterruptiveBot
from src.detectors.context_aware_detector import ContextAwareDetector
from src.interventions.intervention_generator import InterventionGenerator

# 初始化机器人
detector = ContextAwareDetector()
intervention_gen = InterventionGenerator()
bot = InterruptiveBot(detector=detector, intervention_generator=intervention_gen)

# 启动机器人
await bot.start()
```

## 📁 项目结构

```
interruptive_chatbot/
├── src/                     # 源代码
│   ├── core/               # 核心功能模块
│   │   ├── main.py         # 主程序入口
│   │   ├── context_aware_detector.py
│   │   ├── llm_detector.py
│   │   └── explainable_system.py
│   ├── detectors/          # 检测器模块
│   ├── interventions/      # 干预模块
│   ├── models/            # 模型模块
│   └── utils/             # 工具模块
├── tests/                 # 测试文件
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── scenarios/        # 场景测试
├── docs/                 # 文档
├── config/              # 配置文件
├── scripts/            # 脚本文件
├── examples/           # 示例代码
└── data/              # 数据文件
```

详细的项目结构请参考 [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 🧠 核心技术

### Thomas冲突过程模型

基于Thomas的五阶段冲突模型进行智能检测：

1. **挫折感阶段** - 识别初期不满情绪和潜在冲突信号
2. **概念化阶段** - 理解冲突本质和参与者立场
3. **行为阶段** - 检测行为意图（最佳干预时机）
4. **互动阶段** - 监控冲突升级和群体动态
5. **结果阶段** - 评估冲突后果和干预效果

### TKI冲突处理策略

机器人根据冲突类型自动选择合适的处理策略：

- **🤝 协作 (Collaborating)** - 寻求双赢解决方案，满足各方需求
- **🙏 适应 (Accommodating)** - 优先满足他人需求，维护关系
- **💪 竞争 (Competing)** - 坚持自己立场，追求目标达成
- **🚶 回避 (Avoiding)** - 暂时避免冲突，等待适当时机
- **⚖️ 妥协 (Compromising)** - 寻求中间方案，部分满足各方

## 📖 使用指南

### Discord机器人使用

1. **邀请机器人到服务器**
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=2048&scope=bot
   ```

2. **配置权限**
   - 消息读取权限
   - 消息发送权限
   - 嵌入链接权限

3. **开始使用**
   - 机器人会自动监控频道消息
   - 检测到冲突时会自动干预
   - 使用 `!help` 查看命令列表

### 命令行使用

```bash
# 启动机器人
python src/core/main.py

# 运行示例
python examples/basic_usage.py

# 运行测试
python -m pytest tests/

# 代码格式化
black src/ tests/
```

## ⚙️ 配置说明

### 环境变量配置

在 `.env` 文件中配置以下参数：

```env
# Discord 配置
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id

# LLM API 配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# 检测配置
CONFLICT_THRESHOLD=0.8
INTERVENTION_COOLDOWN=30

# 监控配置
MONITORING_ENABLED=true
DASHBOARD_PORT=8080
```

### 配置文件

- `config/settings.yaml` - 项目主要配置
- `config/logging.conf` - 日志配置
- `config/pytest.ini` - 测试配置

## 📚 API文档

### 核心类

#### InterruptiveBot

主要的机器人类，负责协调检测和干预。

```python
class InterruptiveBot:
    def __init__(self, detector, intervention_generator):
        """初始化机器人"""
        
    async def start(self):
        """启动机器人"""
        
    def detect_interruption(self, message):
        """检测是否需要干预"""
        
    def generate_intervention(self, message):
        """生成干预内容"""
```

#### ContextAwareDetector

上下文感知检测器，基于对话历史进行冲突检测。

```python
class ContextAwareDetector:
    def __init__(self, threshold=0.8):
        """初始化检测器"""
        
    def detect(self, message, context):
        """检测冲突"""
        
    def analyze_context(self, conversation_history):
        """分析对话上下文"""
```

详细API文档请参考 [API文档](docs/api/)

## 🛠️ 开发指南

### 开发环境设置

1. **安装开发依赖**
   ```bash
   pip install -e ".[dev]"
   ```

2. **代码格式化**
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

3. **运行测试**
   ```bash
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

3. **添加测试**
   ```python
   # tests/unit/test_my_feature.py
   def test_my_feature():
       # 编写测试用例
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

1. **报告Bug** - 在 [Issues](https://github.com/yourusername/interruptive_chatbot/issues) 中报告问题
2. **提出建议** - 在 [Discussions](https://github.com/yourusername/interruptive_chatbot/discussions) 中提出改进建议
3. **提交代码** - Fork项目并提交Pull Request
4. **改进文档** - 帮助完善文档和示例

### 提交Pull Request

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 开发流程

1. 确保所有测试通过
2. 添加新功能的测试用例
3. 更新相关文档
4. 遵循代码规范

## 📄 许可证

本项目采用 [MIT许可证](LICENSE) - 详见 LICENSE 文件

## 🙏 致谢

- [Thomas-Kilmann冲突模式工具](https://kilmanndiagnostics.com/) - 冲突处理策略理论
- [Discord.py](https://discordpy.readthedocs.io/) - Discord API封装
- [OpenAI](https://openai.com/) - 语言模型服务
- 所有贡献者和用户

## 📞 联系我们

- **项目主页**: [GitHub](https://github.com/yourusername/interruptive_chatbot)
- **问题反馈**: [Issues](https://github.com/yourusername/interruptive_chatbot/issues)
- **讨论交流**: [Discussions](https://github.com/yourusername/interruptive_chatbot/discussions)
- **邮箱**: your.email@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！
