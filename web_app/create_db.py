#!/usr/bin/env python3
"""
创建数据库表
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app import app, db

def create_database():
    """创建数据库表"""
    with app.app_context():
        try:
            db.create_all()
            print("数据库表创建成功!")
            
            # 检查表是否存在
            from app import InterventionStyle
            tables = db.engine.table_names()
            print(f"现有表: {tables}")
            
            # 创建默认风格设置
            default_style = InterventionStyle.query.filter_by(is_active=True).first()
            if not default_style:
                default_style = InterventionStyle(
                    style='collaborating',
                    description='默认协作型风格',
                    is_active=True
                )
                db.session.add(default_style)
                db.session.commit()
                print("默认风格设置已创建")
            else:
                print(f"当前风格设置: {default_style.style}")
                
        except Exception as e:
            print(f"创建数据库表失败: {e}")

if __name__ == "__main__":
    create_database() 