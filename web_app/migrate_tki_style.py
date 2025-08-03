#!/usr/bin/env python3
"""
数据库迁移脚本：为Room表添加TKI风格字段
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# 临时注释掉TKI导入，避免循环导入
import flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 创建临时应用
temp_app = Flask(__name__)
temp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
temp_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
temp_db = SQLAlchemy(temp_app)

# 定义临时的Room模型
class Room(temp_db.Model):
    __tablename__ = 'room'
    id = temp_db.Column(temp_db.Integer, primary_key=True)
    name = temp_db.Column(temp_db.String(100), nullable=False)
    description = temp_db.Column(temp_db.Text)
    max_members = temp_db.Column(temp_db.Integer, default=10)
    is_private = temp_db.Column(temp_db.Boolean, default=False)
    created_by = temp_db.Column(temp_db.Integer, temp_db.ForeignKey('user.id'), nullable=False)
    created_at = temp_db.Column(temp_db.DateTime)
    updated_at = temp_db.Column(temp_db.DateTime)

def migrate_tki_style():
    """添加TKI风格字段到Room表"""
    with temp_app.app_context():
        try:
            # 检查字段是否已存在
            from sqlalchemy import inspect
            inspector = inspect(temp_db.engine)
            columns = [col['name'] for col in inspector.get_columns('room')]
            
            if 'tki_style' not in columns:
                # 添加tki_style字段
                temp_db.engine.execute('ALTER TABLE room ADD COLUMN tki_style VARCHAR(20) DEFAULT "collaborating"')
                print("✅ 已添加tki_style字段到Room表")
            else:
                print("ℹ️ tki_style字段已存在")
            
            # 更新现有房间的默认TKI风格
            rooms = Room.query.all()
            updated_count = 0
            for room in rooms:
                if not hasattr(room, 'tki_style') or room.tki_style is None:
                    room.tki_style = 'collaborating'
                    updated_count += 1
            
            if updated_count > 0:
                temp_db.session.commit()
                print(f"✅ 已更新 {updated_count} 个房间的TKI风格为默认值")
            else:
                print("ℹ️ 所有房间的TKI风格都已设置")
                
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("开始数据库迁移...")
    if migrate_tki_style():
        print("✅ 数据库迁移完成")
    else:
        print("❌ 数据库迁移失败")
        sys.exit(1) 