#!/usr/bin/env python3
"""
测试WebSocket实时更新功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_websocket_update():
    """测试WebSocket实时更新功能"""
    
    print("测试WebSocket实时更新功能...")
    
    # 1. 获取当前风格
    print("\n1. 获取当前风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style")
        if response.status_code == 200:
            data = response.json()
            current_style = data.get('style', 'unknown')
            print(f"   当前风格: {current_style}")
        else:
            print(f"   获取失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   请求失败: {e}")
        return
    
    # 2. 更新风格为协作型
    print("\n2. 更新风格为协作型...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/intervention-style",
            json={"style": "collaborating"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   更新成功: {data.get('style', 'unknown')}")
        else:
            print(f"   更新失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   请求失败: {e}")
        return
    
    # 3. 等待一下让WebSocket事件传播
    print("\n3. 等待WebSocket事件传播...")
    time.sleep(2)
    
    # 4. 再次获取当前风格
    print("\n4. 再次获取当前风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style")
        if response.status_code == 200:
            data = response.json()
            new_style = data.get('style', 'unknown')
            print(f"   当前风格: {new_style}")
            
            if new_style == 'collaborating':
                print("   ✅ WebSocket更新成功!")
            else:
                print("   ❌ WebSocket更新失败!")
        else:
            print(f"   获取失败: {response.status_code}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 5. 恢复原来的风格
    print(f"\n5. 恢复原来的风格: {current_style}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/intervention-style",
            json={"style": current_style},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("   ✅ 风格已恢复")
        else:
            print(f"   ❌ 恢复失败: {response.status_code}")
    except Exception as e:
        print(f"   请求失败: {e}")

if __name__ == "__main__":
    test_websocket_update() 