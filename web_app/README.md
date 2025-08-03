# TKI性别意识智能干预聊天机器人 - Web应用

基于Thomas-Kilmann冲突管理模型的性别结构性边缘化干预系统的Discord风格网页应用。

## 功能特性

- 🎨 **Discord风格界面**: 现代化的聊天界面，类似Discord的用户体验
- 👤 **用户系统**: 完整的注册、登录、登出功能
- 💬 **对话管理**: 创建、管理多个对话会话
- 🤖 **智能干预**: 基于TKI模型的性别意识智能干预
- 📊 **分析报告**: 对话分析和干预策略统计
- 🔒 **安全认证**: JWT令牌认证和密码加密

## 技术栈

### 后端
- **Flask**: Python Web框架
- **SQLAlchemy**: 数据库ORM
- **Flask-Login**: 用户认证
- **bcrypt**: 密码加密
- **PyJWT**: JWT令牌

### 前端
- **HTML5/CSS3**: 现代化界面
- **JavaScript**: 交互逻辑
- **Font Awesome**: 图标库

## 快速开始

### 1. 安装依赖

```bash
cd web_app
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```env
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. 启动应用

#### 方法一：使用启动脚本
```bash
python start_web.py
```

#### 方法二：直接启动
```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：http://localhost:8080

## 使用说明

### 注册新用户
1. 访问应用首页
2. 点击"立即注册"
3. 填写用户名、邮箱和密码
4. 点击注册按钮

### 开始对话
1. 登录后进入主界面
2. 点击"新建对话"或选择现有对话
3. 在消息输入框中输入内容
4. 系统会自动分析并可能提供干预建议

### 查看分析
1. 在侧边栏点击"分析报告"
2. 查看对话的详细分析数据

## API接口

### 认证接口
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `GET /api/logout` - 用户登出

### 对话接口
- `GET /api/conversations` - 获取对话列表
- `POST /api/conversations` - 创建新对话
- `GET /api/conversations/<id>/messages` - 获取对话消息
- `POST /api/conversations/<id>/messages` - 发送消息

### 分析接口
- `GET /api/analysis/<id>` - 获取对话分析

## 数据库结构

### User表
- `id`: 用户ID
- `username`: 用户名
- `email`: 邮箱
- `password_hash`: 密码哈希
- `created_at`: 创建时间

### Conversation表
- `id`: 对话ID
- `user_id`: 用户ID
- `title`: 对话标题
- `created_at`: 创建时间

### Message表
- `id`: 消息ID
- `conversation_id`: 对话ID
- `content`: 消息内容
- `author`: 作者
- `gender`: 性别
- `timestamp`: 时间戳
- `intervention`: 干预内容
- `strategy`: 策略类型

## 开发说明

### 项目结构
```
web_app/
├── app.py              # Flask主应用
├── requirements.txt    # Python依赖
├── start_web.py       # 启动脚本
├── env.example        # 环境变量示例
├── templates/         # HTML模板
│   └── index.html     # 主页面
└── README.md          # 说明文档
```

### 自定义配置

可以通过修改 `app.py` 中的配置来自定义应用：

```python
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
```

### 扩展功能

可以轻松扩展以下功能：
- 用户头像上传
- 实时消息推送
- 文件分享
- 群组聊天
- 消息搜索

## 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **数据库错误**
   ```bash
   # 删除数据库文件重新创建
   rm chatbot.db
   python app.py
   ```

3. **端口被占用**
   ```bash
   # 修改端口
   app.run(debug=True, host='0.0.0.0', port=8080)
   ```

## 许可证

本项目基于原有TKI项目的许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。 