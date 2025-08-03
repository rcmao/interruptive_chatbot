#!/usr/bin/env python3
"""
数据库迁移脚本：将默认干预风格从collaborating改为none
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app import app, db, InterventionStyle
from datetime import datetime

def migrate_default_style():
    """迁移默认风格设置"""
    with app.app_context():
        try:
            # 查找现有的干预风格设置
            existing_settings = InterventionStyle.query.filter_by(is_active=True).all()
            
            if existing_settings:
                print(f"找到 {len(existing_settings)} 个活跃的干预风格设置")
                
                for setting in existing_settings:
                    if setting.style == 'collaborating':
                        print(f"将风格从 'collaborating' 更新为 'none'")
                        setting.style = 'none'
                        setting.description = '默认无插话风格'
                        setting.updated_at = datetime.now()
                    else:
                        print(f"保持现有风格: {setting.style}")
            else:
                print("没有找到现有的干预风格设置，创建默认设置")
                default_setting = InterventionStyle(
                    style='none',
                    description='默认无插话风格',
                    is_active=True
                )
                db.session.add(default_setting)
            
            db.session.commit()
            print("数据库迁移完成！")
            
        except Exception as e:
            print(f"迁移失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_default_style() 