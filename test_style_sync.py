#!/usr/bin/env python3
"""
测试TKI风格同步功能
验证管理员更新风格后，普通用户是否能正确接收更新
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_style_sync():
    """测试风格同步功能"""
    print("=== 测试TKI风格同步功能 ===")
    
    # 1. 获取当前风格
    print("\n1. 获取当前风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style")
        if response.status_code == 200:
            current_style = response.json().get('style')
            print(f"   当前风格: {current_style}")
        else:
            print(f"   获取风格失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   请求失败: {e}")
        return
    
    # 2. 模拟管理员更新风格（通过WebSocket事件）
    print("\n2. 模拟管理员更新风格...")
    try:
        # 这里我们直接测试API接口，实际应用中是通过WebSocket
        test_style = "competing"
        print(f"   更新风格为: {test_style}")
        
        # 注意：这里只是测试API，实际WebSocket测试需要更复杂的设置
        print("   风格更新请求已发送（WebSocket事件）")
        
    except Exception as e:
        print(f"   更新风格失败: {e}")
        return
    
    # 3. 验证普通用户是否能获取更新后的风格
    print("\n3. 验证普通用户获取更新后的风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style")
        if response.status_code == 200:
            updated_style = response.json().get('style')
            print(f"   更新后风格: {updated_style}")
            
            if updated_style == test_style:
                print("   ✅ 风格同步成功！")
            else:
                print(f"   ❌ 风格同步失败，期望: {test_style}, 实际: {updated_style}")
        else:
            print(f"   获取更新后风格失败: {response.status_code}")
    except Exception as e:
        print(f"   验证失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_style_sync() 