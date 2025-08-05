#!/usr/bin/env python3
"""
多语言翻译文件
支持中文和英文切换
"""

TRANSLATIONS = {
    "zh": {
        # 页面标题
        "page_title": "TKI性别意识智能干预聊天机器人",
        "app_title": "TKI智能干预机器人",
        "app_subtitle": "基于Thomas-Kilmann冲突管理模型的性别结构性边缘化干预系统",
        
        # 认证相关
        "login": "登录",
        "register": "注册",
        "logout": "登出",
        "username": "用户名",
        "email": "邮箱",
        "password": "密码",
        "confirm_password": "确认密码",
        "login_username_placeholder": "请输入用户名",
        "login_password_placeholder": "请输入密码",
        "register_username_placeholder": "请输入用户名",
        "register_email_placeholder": "请输入邮箱",
        "register_password_placeholder": "请输入密码",
        "register_confirm_password_placeholder": "请再次输入密码",
        "invite_code": "邀请码",
        "invite_code_placeholder": "请输入邀请码（可选）",
        "invite_code_required": "邀请码是必需的",
        "invite_code_invalid": "邀请码无效",
        "login_success": "登录成功！",
        "register_success": "注册成功！",
        "login_failed": "登录失败，请重试",
        "register_failed": "注册失败，请重试",
        "username_exists": "用户名已存在",
        "email_exists": "邮箱已存在",
        "invalid_credentials": "用户名或密码错误",
        "missing_fields": "请填写所有字段",
        "no_account": "还没有账号？",
        "has_account": "已有账号？",
        "register_now": "立即注册",
        "login_now": "立即登录",
        
        # 导航菜单
        "conversations": "对话列表",
        "analysis": "分析报告",
        "new_conversation": "新建对话",
        "settings": "设置",
        "language": "语言",
        
        # 对话相关
        "select_conversation": "选择或创建一个对话开始聊天",
        "new_conversation_title": "新对话",
        "conversation_title": "对话标题",
        "message_count": "条消息",
        "send_message": "发送消息",
        "message_placeholder": "输入消息...",
        "no_conversation": "请先选择一个对话",
        "create_conversation": "创建新对话",
        "delete_conversation": "删除对话",
        "rename_conversation": "重命名对话",
        
        # 消息相关
        "message_sent": "消息发送成功",
        "message_failed": "发送失败，请重试",

        
        # 分析相关
        "analysis_report": "分析报告",
        "conversation_analysis": "对话分析",
        "metrics": "指标",
        "total_messages": "总消息数",
        "female_messages": "女性消息数",
        "male_messages": "男性消息数",
        
        # 用户界面
        "loading": "加载中...",
        "error": "错误",
        "success": "成功",
        "warning": "警告",
        "info": "信息",
        "confirm": "确认",
        "cancel": "取消",
        "save": "保存",
        "edit": "编辑",
        "delete": "删除",
        "close": "关闭",
        "back": "返回",
        "next": "下一步",
        "previous": "上一步",
        
        # 时间相关
        "just_now": "刚刚",
        "minutes_ago": "分钟前",
        "hours_ago": "小时前",
        "days_ago": "天前",
        "today": "今天",
        "yesterday": "昨天",
        
        # 错误消息
        "network_error": "网络错误，请检查连接",
        "server_error": "服务器错误，请稍后重试",
        "timeout_error": "请求超时，请重试",
        "unknown_error": "未知错误",
        "file_too_large": "文件过大",
        "invalid_format": "格式无效",
        
        # 提示消息
        "welcome_message": "欢迎使用聊天室系统！",
        "help_message": "点击左侧菜单开始使用",
        "no_messages": "暂无消息",
        "no_conversations": "暂无对话",
        "creating_conversation": "正在创建对话...",
        "sending_message": "正在发送消息...",
        "loading_messages": "正在加载消息...",
        "loading_conversations": "正在加载对话列表...",
        
        # 设置相关
        "settings_title": "设置",
        "language_settings": "语言设置",
        "theme_settings": "主题设置",
        "notification_settings": "通知设置",
        "privacy_settings": "隐私设置",
        "account_settings": "账户设置",
        
        # 主题
        "light_theme": "浅色主题",
        "dark_theme": "深色主题",
        "auto_theme": "自动主题",
        
        # 通知
        "enable_notifications": "启用通知",
        "message_notifications": "消息通知",

        "sound_notifications": "声音通知",
        
        # 隐私
        "data_privacy": "数据隐私",
        "conversation_privacy": "对话隐私",
        "analytics_privacy": "分析隐私",
        
        # 账户
        "profile": "个人资料",
        "change_password": "修改密码",
        "delete_account": "删除账户",
        "export_data": "导出数据",
        
        # 其他
        "version": "版本",
        "about": "关于",
        "help": "帮助",
        "feedback": "反馈",
        "support": "支持",
        "terms": "条款",
        "privacy": "隐私",
        "contact": "联系",
    },
    
    "en": {
        # Page titles
        "page_title": "TKI Gender-Aware Intelligent Intervention Chatbot",
        "app_title": "TKI Intelligent Intervention Bot",
        "app_subtitle": "Gender Structural Marginalization Intervention System Based on Thomas-Kilmann Conflict Management Model",
        
        # Authentication
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "login_username_placeholder": "Enter username",
        "login_password_placeholder": "Enter password",
        "register_username_placeholder": "Enter username",
        "register_email_placeholder": "Enter email",
        "register_password_placeholder": "Enter password",
        "register_confirm_password_placeholder": "Confirm password",
        "invite_code": "Invite Code",
        "invite_code_placeholder": "Enter invite code (optional)",
        "invite_code_required": "Invite code is required",
        "invite_code_invalid": "Invalid invite code",
        "login_success": "Login successful!",
        "register_success": "Registration successful!",
        "login_failed": "Login failed, please try again",
        "register_failed": "Registration failed, please try again",
        "username_exists": "Username already exists",
        "email_exists": "Email already exists",
        "invalid_credentials": "Invalid username or password",
        "missing_fields": "Please fill in all fields",
        "no_account": "Don't have an account?",
        "has_account": "Already have an account?",
        "register_now": "Register now",
        "login_now": "Login now",
        
        # Navigation menu
        "conversations": "Conversations",
        "analysis": "Analysis",
        "new_conversation": "New Conversation",
        "settings": "Settings",
        "language": "Language",
        
        # Conversations
        "select_conversation": "Select or create a conversation to start chatting",
        "new_conversation_title": "New Conversation",
        "conversation_title": "Conversation Title",
        "message_count": "messages",
        "send_message": "Send Message",
        "message_placeholder": "Type a message...",
        "no_conversation": "Please select a conversation first",
        "create_conversation": "Create New Conversation",
        "delete_conversation": "Delete Conversation",
        "rename_conversation": "Rename Conversation",
        
        # Messages
        "message_sent": "Message sent successfully",
        "message_failed": "Failed to send message, please try again",

        
        # Analysis
        "analysis_report": "Analysis Report",
        "conversation_analysis": "Conversation Analysis",
        "metrics": "Metrics",
        "total_messages": "Total Messages",
        "female_messages": "Female Messages",
        "male_messages": "Male Messages",
        
        # User interface
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "save": "Save",
        "edit": "Edit",
        "delete": "Delete",
        "close": "Close",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        
        # Time
        "just_now": "Just now",
        "minutes_ago": "minutes ago",
        "hours_ago": "hours ago",
        "days_ago": "days ago",
        "today": "Today",
        "yesterday": "Yesterday",
        
        # Error messages
        "network_error": "Network error, please check connection",
        "server_error": "Server error, please try again later",
        "timeout_error": "Request timeout, please try again",
        "unknown_error": "Unknown error",
        "file_too_large": "File too large",
        "invalid_format": "Invalid format",
        
        # Tips
        "welcome_message": "Welcome to Chat Room System!",
        "help_message": "Click the left menu to get started",
        "no_messages": "No messages",
        "no_conversations": "No conversations",
        "creating_conversation": "Creating conversation...",
        "sending_message": "Sending message...",
        "loading_messages": "Loading messages...",
        "loading_conversations": "Loading conversations...",
        
        # Settings
        "settings_title": "Settings",
        "language_settings": "Language Settings",
        "theme_settings": "Theme Settings",
        "notification_settings": "Notification Settings",
        "privacy_settings": "Privacy Settings",
        "account_settings": "Account Settings",
        
        # Themes
        "light_theme": "Light Theme",
        "dark_theme": "Dark Theme",
        "auto_theme": "Auto Theme",
        
        # Notifications
        "enable_notifications": "Enable Notifications",
        "message_notifications": "Message Notifications",

        "sound_notifications": "Sound Notifications",
        
        # Privacy
        "data_privacy": "Data Privacy",
        "conversation_privacy": "Conversation Privacy",
        "analytics_privacy": "Analytics Privacy",
        
        # Account
        "profile": "Profile",
        "change_password": "Change Password",
        "delete_account": "Delete Account",
        "export_data": "Export Data",
        
        # Others
        "version": "Version",
        "about": "About",
        "help": "Help",
        "feedback": "Feedback",
        "support": "Support",
        "terms": "Terms",
        "privacy": "Privacy",
        "contact": "Contact",
    }
}

def get_text(key, lang="zh"):
    """获取翻译文本"""
    if lang not in TRANSLATIONS:
        lang = "zh"  # 默认中文
    
    return TRANSLATIONS[lang].get(key, key)

def get_language_list():
    """获取支持的语言列表"""
    return [
        {"code": "zh", "name": "中文", "flag": "🇨🇳"},
        {"code": "en", "name": "English", "flag": "🇺🇸"}
    ] 