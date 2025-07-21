# Interruptive Chatbot

一个基于Discord的智能聊天机器人，用于检测和调解群聊中的冲突。

## 功能特性

- 🤖 **冲突检测**: 使用OpenAI API实时分析群聊消息，检测冲突程度
- 🛡️ **智能干预**: 当检测到激烈讨论时，自动发送调解消息
- 📊 **评分系统**: 1-10分冲突评分机制，精确判断干预时机
- 🔄 **历史记录**: 维护最近8条消息的历史记录进行分析

## 技术栈

- **Python 3.8+**
- **Discord.py** - Discord机器人框架
- **OpenAI API** - 支持第三方API调用
- **python-dotenv** - 环境变量管理

## 安装和配置

### 1. 克隆项目
```bash
git clone https://github.com/rcmao/interruptive_chatbot.git
cd interruptive_chatbot
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
创建 `.env` 文件并配置以下变量：
```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_openai_api_base_url
```

### 4. 运行机器人
```bash
python main.py
```

## 工作原理

1. **消息监听**: 机器人监听Discord频道中的所有消息
2. **历史记录**: 维护最近8条消息的历史记录
3. **冲突分析**: 当有足够消息时，使用OpenAI API分析冲突程度
4. **智能干预**: 当冲突评分≥7时，发送调解消息

## 冲突评分标准

- **1-3分**: 正常讨论
- **4-6分**: 观点分歧，轻微紧张
- **7-8分**: 情绪化表达，需要干预
- **9-10分**: 激烈冲突，急需调解

## 项目结构

```
interruptive_chatbot/
├── main.py              # 主程序文件
├── requirements.txt      # 依赖包列表
├── .env                 # 环境变量配置（不提交到git）
├── .gitignore          # Git忽略文件
└── README.md           # 项目说明文档
```

## 注意事项

- 确保Discord机器人有适当的权限
- OpenAI API需要有效的API密钥
- 支持第三方OpenAI API服务
- 敏感信息（如API密钥）不会提交到git

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！ 