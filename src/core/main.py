#!/usr/bin/env python3
"""
智能冲突干预聊天机器人 - 主入口点
"""

import sys
import os
import asyncio

# 添加src到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    try:
        from core.main import main
        asyncio.run(main())
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请确保所有依赖已安装: pip install -r config/requirements.txt")
        print(f" 当前路径: {current_dir}")
        print(f"📁 src路径: {src_path}")
    except Exception as e:
        print(f"❌ 启动失败: {e}")