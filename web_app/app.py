import os
import sys
import json
import random
import aiohttp
from datetime import datetime, timedelta
from collections import deque

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import logging
from flask_cors import CORS
import pytz

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入翻译模块
try:
    from translations import get_text, get_language_list
except ImportError as e:
    logger.error(f"导入翻译模块失败: {e}")
    # 创建简单的翻译函数
    def get_text(key, lang='zh'):
        return key
    
    def get_language_list():
        return ['zh', 'en']

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatroom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

# 设置时区
def get_local_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

# 数据库模型定义
class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'admin' 或 'member'
    is_active = db.Column(db.Boolean, default=True)
    gender = db.Column(db.String(10), default='unknown')  # 'male', 'female', 'unknown'
    avatar = db.Column(db.String(200), default='')
    display_name = db.Column(db.String(100), default='')  # 显示名称
    bio = db.Column(db.Text, default='')  # 个人简介
    status = db.Column(db.String(20), default='online')  # 'online', 'offline', 'busy'
    created_at = db.Column(db.DateTime, default=get_local_time)
    last_seen = db.Column(db.DateTime, default=get_local_time)
    
    # 关系
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    messages = db.relationship('Message', backref='user', lazy=True)
    room_memberships = db.relationship('RoomMembership', backref='user', lazy=True)
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == 'admin'
    
    def is_member(self):
        """检查是否为普通成员"""
        return self.role == 'member'
    
    def can_access_user_data(self, user_id):
        """检查是否可以访问用户数据"""
        return self.is_admin() or self.id == user_id
    
    def can_manage_rooms(self):
        """检查是否可以管理房间"""
        return self.is_admin()
    
    def can_manage_members(self):
        """检查是否可以管理成员"""
        return self.is_admin()
    
    def can_view_statistics(self):
        """检查是否可以查看统计"""
        return self.is_admin()
    
    def can_export_data(self):
        """检查是否可以导出数据"""
        return self.is_admin()
    
    def can_manage_tests(self):
        """检查是否可以管理测试"""
        return self.is_admin()

class Room(db.Model):
    """房间模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    max_members = db.Column(db.Integer, default=10)
    is_private = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_local_time)
    updated_at = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)
    
    # 关系
    members = db.relationship('RoomMembership', backref='room', lazy=True)
    messages = db.relationship('Message', backref='room', lazy=True)

class RoomMembership(db.Model):
    """房间成员关系"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'admin' 或 'member'
    joined_at = db.Column(db.DateTime, default=get_local_time)
    is_online = db.Column(db.Boolean, default=False)
    can_send_messages = db.Column(db.Boolean, default=True)
    can_edit_messages = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'room_id', name='unique_user_room'),)
    
    def is_room_admin(self):
        """检查是否为房间管理员"""
        return self.role == 'admin'
    
    def is_room_member(self):
        """检查是否为房间成员"""
        return self.role == 'member'

class Conversation(db.Model):
    """对话模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_local_time)
    updated_at = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)
    messages = db.relationship('Message', backref='conversation', lazy=True)

class Message(db.Model):
    """消息模型"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10), default='unknown')
    timestamp = db.Column(db.DateTime, default=get_local_time)
    
    # 关联字段
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 管理员权限装饰器
def jwt_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '缺少认证token'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': '用户不存在'}), 401
            # 将用户设置为当前用户
            from flask_login import login_user
            login_user(user)
            # 将用户ID存储到session中，供WebSocket使用
            session['user_id'] = user.id
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的Token'}), 401
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 创建数据库表
with app.app_context():
    db.create_all()

# 路由定义
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/test')
def test_register():
    """注册功能测试页面"""
    return render_template('test_register.html')

@app.route('/test-links')
def test_links():
    """链接功能测试页面"""
    return render_template('test_links.html')

@app.route('/register')
def register_page():
    """用户注册页面"""
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """数据统计仪表板"""
    return render_template('dashboard.html')

@app.route('/rooms')
def rooms():
    """房间管理页面"""
    return render_template('rooms.html')

@app.route('/chat/<room_id>')
def chat_room(room_id):
    """聊天房间页面"""
    # 检查房间是否存在
    room = Room.query.get(room_id)
    if not room:
        return render_template('error.html', 
                             error_message='房间不存在或已被删除',
                             back_url='/rooms')
    
    return render_template('chat_room.html', room_id=room_id)

# API路由
@app.route('/api/language', methods=['GET'])
def get_languages():
    """获取支持的语言列表"""
    return jsonify(get_language_list())

@app.route('/api/translations/<lang>', methods=['GET'])
def get_translations(lang):
    """获取指定语言的翻译"""
    return jsonify(get_text(lang))

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 处理邀请码
    invite_code = data.get('invite_code', '')
    role = 'user'  # 默认为普通用户
    
    if invite_code == 'ADMIN2024':
        role = 'admin'
    elif invite_code and invite_code != 'PUBLIC':
        return jsonify({'error': '邀请码无效'}), 400
    
    # 创建用户
    password_hash = generate_password_hash(data['password'])
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash,
        role=role,
        gender=data.get('gender', 'unknown')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # 生成JWT token
    token = jwt.encode(
                    {'user_id': user.id, 'exp': get_local_time() + timedelta(days=7)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return jsonify({
        'message': '注册成功',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'gender': user.gender
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': '缺少必要字段'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        # 更新最后在线时间
        user.last_seen = get_local_time()
        user.status = 'online'
        db.session.commit()
        
        # 生成JWT token
        token = jwt.encode(
            {'user_id': user.id, 'exp': get_local_time() + timedelta(days=7)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'gender': user.gender
            }
        })
    else:
        return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    # 更新用户状态
    if current_user.is_authenticated:
        current_user.status = 'offline'
        current_user.last_seen = get_local_time()
        db.session.commit()
    
    return jsonify({'message': '登出成功'})

# 房间相关API
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """获取房间列表"""
    rooms = Room.query.all()
    room_list = [{
        'id': room.id,
        'name': room.name,
        'description': room.description,
        'member_count': len(room.members),
        'max_members': room.max_members,
        'created_at': room.created_at.isoformat()
    } for room in rooms]
    
    print(f'返回房间列表: {room_list}')
    return jsonify(room_list)

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """创建新房间"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': '房间名称不能为空'}), 400
    
    room = Room(
        name=data['name'],
        description=data.get('description', ''),
        max_members=data.get('max_members', 10),
        is_private=data.get('is_private', False),
        created_by=current_user.id if current_user.is_authenticated else 1
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({
        'id': room.id,
        'name': room.name,
        'description': room.description,
        'created_at': room.created_at.isoformat()
    }), 201

@app.route('/api/rooms/<int:room_id>/join', methods=['POST'])
@jwt_required
def join_room(room_id):
    """加入房间"""
    room = Room.query.get_or_404(room_id)
    
    # 检查是否已经是成员
    existing_membership = RoomMembership.query.filter_by(
        user_id=current_user.id, room_id=room_id
    ).first()
    
    if existing_membership:
        existing_membership.is_online = True
        db.session.commit()
        return jsonify({'message': '已重新加入房间'})
    
    # 检查房间是否已满
    if len(room.members) >= room.max_members:
        return jsonify({'error': '房间已满'}), 400
    
    membership = RoomMembership(user_id=current_user.id, room_id=room_id, is_online=True)
    db.session.add(membership)
    db.session.commit()
    
    return jsonify({'message': '成功加入房间'})

@app.route('/api/rooms/<int:room_id>/leave', methods=['POST'])
@jwt_required
def leave_room(room_id):
    """离开房间"""
    room = Room.query.get_or_404(room_id)
    
    # 查找用户的成员关系
    membership = RoomMembership.query.filter_by(
        user_id=current_user.id, room_id=room_id
    ).first()
    
    if membership:
        # 设置用户在该房间为离线状态
        membership.is_online = False
        db.session.commit()
        
        return jsonify({'message': '已离开房间'})
    else:
        return jsonify({'error': '您不是该房间的成员'}), 400

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
@jwt_required
def get_room(room_id):
    """获取房间信息"""
    room = Room.query.get_or_404(room_id)
    return jsonify({
        'id': room.id,
        'name': room.name,
        'description': room.description,
        'max_members': room.max_members,
        'member_count': len(room.members),
        'created_at': room.created_at.isoformat()
    })

@app.route('/api/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """更新房间信息"""
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少数据'}), 400
    
    try:
        if 'name' in data:
            room.name = data['name']
        if 'description' in data:
            room.description = data['description']
        if 'max_members' in data:
            room.max_members = data['max_members']
        if 'is_private' in data:
            room.is_private = data['is_private']
        
        room.updated_at = get_local_time()
        db.session.commit()
        
        return jsonify({
            'message': '房间更新成功',
            'room': {
                'id': room.id,
                'name': room.name,
                'description': room.description,
                'max_members': room.max_members,
                'is_private': room.is_private,
                'created_by': room.created_by,
                'created_at': room.created_at.isoformat(),
                'member_count': len(room.members)
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"更新房间失败: {e}")
        return jsonify({'error': '更新失败'}), 500

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """删除房间"""
    room = Room.query.get_or_404(room_id)
    
    try:
        # 删除房间相关的所有数据
        # 删除房间成员关系
        RoomMembership.query.filter_by(room_id=room_id).delete()
        
        # 删除房间消息
        Message.query.filter_by(room_id=room_id).delete()
        
        # 删除房间本身
        db.session.delete(room)
        db.session.commit()
        
        return jsonify({'message': '房间删除成功'})
    except Exception as e:
        db.session.rollback()
        print(f"删除房间失败: {e}")
        return jsonify({'error': '删除失败'}), 500

@app.route('/api/rooms/<int:room_id>/messages', methods=['GET'])
@jwt_required
def get_room_messages(room_id):
    """获取房间消息"""
    messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp).all()
    message_list = []
    
    for msg in messages:
        # 获取用户头像
        user_avatar = ''
        if msg.user_id:
            user = User.query.get(msg.user_id)
            if user:
                user_avatar = user.avatar
        
        message_list.append({
            'id': msg.id,
            'content': msg.content,
            'author': msg.author,
            'avatar': user_avatar,
            'timestamp': msg.timestamp.isoformat()
        })
    
    return jsonify(message_list)

@app.route('/api/rooms/<int:room_id>/messages', methods=['POST'])
@jwt_required
def send_message(room_id):
    """发送消息到房间"""
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': '消息内容不能为空'}), 400
    
    # 创建消息
    message = Message(
        content=data['content'],
        author=current_user.display_name or current_user.username,
        gender=current_user.gender,
        room_id=room_id,
        user_id=current_user.id
    )
    
    db.session.add(message)
    db.session.commit()
    
    # 通过WebSocket广播消息到房间
    message_data = {
        'id': message.id,
        'content': message.content,
        'author': message.author,
        'avatar': current_user.avatar,  # 添加用户头像
        'timestamp': message.timestamp.isoformat()
    }
    
    # 发送消息到房间
    socketio.emit('message', message_data, room=str(room_id))
    
    return jsonify(message_data), 201

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取当前用户信息"""
    # 检查JWT token
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.query.get(user_id)
            if user:
                return jsonify({
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'email': user.email,
                    'gender': user.gender,
                    'bio': user.bio,
                    'avatar': user.avatar,
                    'role': user.role,
                    'status': user.status,
                    'created_at': user.created_at.isoformat(),
                    'message_count': len(user.messages),
                    'room_count': len(user.room_memberships)
                })
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的Token'}), 401
    
    # 如果JWT token无效，检查session认证
    if not current_user.is_authenticated:
        return jsonify({'error': '未登录'}), 401
    
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'display_name': current_user.display_name,
        'email': current_user.email,
        'gender': current_user.gender,
        'bio': current_user.bio,
        'avatar': current_user.avatar,
        'role': current_user.role,
        'status': current_user.status,
        'created_at': current_user.created_at.isoformat(),
        'message_count': len(current_user.messages),
        'room_count': len(current_user.room_memberships)
    })

@app.route('/api/stats/<int:room_id>', methods=['GET'])
def get_room_stats(room_id):
    """获取房间统计数据"""
    room = Room.query.get_or_404(room_id)
    
    # 获取今日统计
    today = get_local_time().date()
    # 由于没有冲突检测，这里只统计消息数量
    total_messages = Message.query.filter_by(room_id=room_id).count()
    
    return jsonify({
        'total_messages': total_messages,
        'male_messages': 0, # 没有冲突检测，无法统计性别
        'female_messages': 0,
        'male_percentage': 0,
        'female_percentage': 0
    })

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """获取仪表板统计数据"""
    # 计算总体统计
    total_messages = Message.query.count()
    
    # 性别分布
    male_messages = Message.query.filter_by(gender='male').count()
    female_messages = Message.query.filter_by(gender='female').count()
    unknown_messages = Message.query.filter_by(gender='unknown').count()
    
    return jsonify({
        'totalMessages': total_messages,
        'messageChange': '+12',
        'genderDistribution': {
            'male': male_messages,
            'female': female_messages,
            'unknown': unknown_messages
        }
    })

@app.route('/api/dashboard/activity', methods=['GET'])
def get_dashboard_activity():
    """获取最近活动"""
    # 获取最近的消息
    recent_messages = Message.query.order_by(Message.timestamp.desc()).limit(10).all()
    
    activities = []
    
    # 添加消息活动
    for msg in recent_messages:
        activities.append({
            'type': 'message',
            'text': f'{msg.author} 发送了消息',
            'timestamp': msg.timestamp.isoformat()
        })
    
    # 按时间排序
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(activities[:15])  # 返回最近15个活动

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    users = User.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'display_name': user.display_name,
        'gender': user.gender,
        'status': user.status,
        'role': user.role,
        'avatar': user.avatar
    } for user in users])

@app.route('/api/rooms/<int:room_id>/members', methods=['GET'])
@jwt_required
def get_room_members(room_id):
    """获取房间成员列表"""
    room = Room.query.get_or_404(room_id)
    members = []
    
    for membership in room.members:
        user = User.query.get(membership.user_id)
        if user:
            members.append({
                'user_id': user.id,
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'gender': user.gender,
                'avatar': user.avatar,
                'role': membership.role,
                'is_online': membership.is_online,
                'joined_at': membership.joined_at.isoformat()
            })
    
    return jsonify(members)

@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """更新用户资料"""
    # 检查JWT token
    auth_header = request.headers.get('Authorization')
    user = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            user = User.query.get(user_id)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的Token'}), 401
    
    # 如果JWT token无效，检查session认证
    if not user and not current_user.is_authenticated:
        return jsonify({'error': '未登录'}), 401
    
    if not user:
        user = current_user
    
    try:
        # 获取表单数据
        display_name = request.form.get('display_name', '')
        gender = request.form.get('gender', 'unknown')
        
        # 允许修改显示名称、性别和头像，其他字段保持不变
        
        # 处理头像上传
        avatar_path = user.avatar  # 保持原头像
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and avatar_file.filename:
                # 创建上传目录
                upload_dir = os.path.join(app.root_path, 'static', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                
                # 生成文件名
                filename = f"avatar_{user.id}_{int(get_local_time().timestamp())}.jpg"
                filepath = os.path.join(upload_dir, filename)
                
                # 保存文件
                avatar_file.save(filepath)
                avatar_path = f"/static/avatars/{filename}"
        
        # 更新用户信息（更新显示名称、性别和头像）
        user.display_name = display_name
        user.gender = gender
        user.avatar = avatar_path
        
        db.session.commit()
        
        return jsonify({
            'message': '资料更新成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'email': user.email,
                'gender': user.gender,
                'bio': user.bio,
                'avatar': user.avatar,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'message_count': len(user.messages),
                'room_count': len(user.room_memberships)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"更新用户资料失败: {e}")
        return jsonify({'error': '更新失败'}), 500

@app.route('/profile')
def profile():
    """用户资料页面"""
    return render_template('profile.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    """管理员控制面板"""
    return render_template('admin_dashboard.html')

@app.route('/test-admin-style')
def test_admin_style():
    """测试admin风格切换功能"""
    return render_template('test_admin_style.html')

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """处理WebSocket连接"""
    print(f'客户端连接: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """处理WebSocket断开"""
    print(f'客户端断开: {request.sid}')

@socketio.on('echo')
def handle_echo(data):
    """简单的echo测试"""
    print(f'收到echo事件: {data}')
    emit('echo', {'response': '服务器收到echo', 'data': data})

@socketio.on('test')
def handle_test(data):
    """测试WebSocket连接"""
    print(f'收到测试消息: {data}')
    # 回复测试消息
    emit('test', {'message': '服务器收到测试消息', 'data': data})

@socketio.on('join_room')
def handle_join_room(data):
    """处理加入房间事件"""
    print(f'收到加入房间事件: {data}')
    room = data.get('room')
    if room:
        join_room(room)
        print(f'用户已加入房间: {room}')
        # 通知其他用户有新用户加入
        socketio.emit('user_joined', {
            'room': room,
            'user_id': session.get('user_id'),
            'timestamp': datetime.now().isoformat()
        }, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    """处理离开房间事件"""
    print(f'收到离开房间事件: {data}')
    room = data.get('room')
    if room:
        leave_room(room)
        print(f'用户已离开房间: {room}')
        # 通知其他用户有用户离开
        socketio.emit('user_left', {
            'room': room,
            'user_id': session.get('user_id'),
            'timestamp': datetime.now().isoformat()
        }, room=room)

# TKI风格选择功能已移除

@socketio.on('send_message')
def handle_send_message(data):
    """处理发送消息"""
    room = data.get('room')
    message_data = data.get('message')
    
    if not room or not message_data:
        return
    
    # 获取用户信息
    user_id = session.get('user_id')
    
    if not user_id and current_user.is_authenticated:
        user_id = current_user.id
    
    # 如果没有用户ID，使用默认用户
    if not user_id:
        user = User.query.first()
        if not user:
            user = User(
                username='test_user',
                email='test@example.com',
                password_hash='test',
                display_name='测试用户',
                gender='unknown'
            )
            db.session.add(user)
            db.session.commit()
    else:
        user = User.query.get(user_id)
        if not user:
            return
    
    # 创建消息记录
    message = Message(
        content=message_data['content'],
        author=user.display_name or user.username,
        gender=user.gender,
        room_id=int(room),
        user_id=user.id
    )
    
    db.session.add(message)
    db.session.commit()
    
    # 构建消息数据
    message_info = {
        'id': message.id,
        'content': message.content,
        'author': message.author,
        'avatar': user.avatar,
        'timestamp': message.timestamp.isoformat()
    }
    
    # 广播消息到房间
    room = str(room)
    socketio.emit('message', message_info, room=room)

@socketio.on('chat_message')
async def handle_chat_message(data):
    """处理发送消息 - 兼容旧的事件名"""
    room = data.get('room')
    message_data = data.get('message')
    
    if not room or not message_data:
        return
    
    # 获取用户信息
    user_id = session.get('user_id')
    
    if not user_id and current_user.is_authenticated:
        user_id = current_user.id
    
    # 如果没有用户ID，使用默认用户
    if not user_id:
        user = User.query.first()
        if not user:
            user = User(
                username='test_user',
                email='test@example.com',
                password_hash='test',
                display_name='测试用户',
                gender='unknown'
            )
            db.session.add(user)
            db.session.commit()
    else:
        user = User.query.get(user_id)
        if not user:
            return
    
    # 创建消息记录
    message = Message(
        content=message_data['content'],
        author=user.display_name or user.username,
        gender=user.gender,
        room_id=int(room),
        user_id=user.id
    )
    
    db.session.add(message)
    db.session.commit()
    
    # 构建消息数据
    message_info = {
        'id': message.id,
        'content': message.content,
        'author': message.author,
        'avatar': user.avatar,
        'timestamp': message.timestamp.isoformat()
    }
    
    # 广播消息到房间
    room = str(room)
    socketio.emit('message', message_info, room=room)

@app.route('/test_broadcast')
def test_broadcast():
    """测试广播消息"""
    return "测试广播功能"

@app.route('/test_chat')
def test_chat():
    """测试聊天页面"""
    return render_template('test_chat_simple.html')

@app.route('/test_send_message', methods=['POST'])
def test_send_message():
    """测试消息发送端点"""
    try:
        data = request.get_json()
        room_id = data.get('room_id', 1)
        content = data.get('content', '测试消息')
        author = data.get('author', '测试用户')
        
        # 创建消息记录
        message = Message(
            content=content,
            author=author,
            gender='unknown',
            room_id=room_id,
            user_id=1
        )
        
        db.session.add(message)
        db.session.commit()
        
        # 构建消息数据
        message_info = {
            'id': message.id,
            'content': message.content,
            'author': message.author,
            'avatar': '',
            'timestamp': message.timestamp.isoformat()
        }
        
        # 广播消息
        room = str(room_id)
        socketio.emit('message', message_info, room=room)
        socketio.emit('message', message_info)
        
        return jsonify({'success': True, 'message': message_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8081)