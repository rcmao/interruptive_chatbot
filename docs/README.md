# 智能冲突干预聊天机器人

## 项目概述
基于Thomas冲突过程模型和TKI策略的智能冲突干预系统

## 项目结构
```
interruptive_chatbot/
├── src/core/           # 核心系统
├── src/detectors/      # 冲突检测器
├── src/interventions/  # 干预策略
├── tests/              # 测试文件
├── config/             # 配置文件
├── docs/               # 文档
└── scripts/            # 脚本
```

## 快速开始
1. 安装依赖: `pip install -r config/requirements.txt`
2. 配置环境: 复制 `config/.env.example` 到 `config/.env`
3. 运行测试: `python scripts/run_tests.sh`
4. 启动机器人: `python src/core/main.py`

## 核心功能
- 智能冲突检测
- 场景感知策略选择
- Slot-based干预生成
- 实时交互集成

## 技术栈
- Python 3.8+
- OpenAI GPT API
- Discord.py
- Thomas-Kilmann Instrument (TKI)