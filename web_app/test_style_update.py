#!/usr/bin/env python3
"""
测试干预风格更新功能
"""

import requests
import json

BASE_URL = "http://localhost:8081"

def test_style_update():
    """测试风格更新功能"""
    
    # 1. 获取当前风格
    print("1. 获取当前风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style")
        if response.status_code == 200:
            data = response.json()
            print(f"   当前风格: {data.get('style', 'unknown')}")
        else:
            print(f"   获取失败: {response.status_code}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 2. 更新风格为竞争型
    print("\n2. 更新风格为竞争型...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/intervention-style",
            json={"style": "competing"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   更新成功: {data.get('style', 'unknown')}")
        else:
            print(f"   更新失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 3. 再次获取当前风格
    print("\n3. 再次获取当前风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style")
        if response.status_code == 200:
            data = response.json()
            print(f"   当前风格: {data.get('style', 'unknown')}")
        else:
            print(f"   获取失败: {response.status_code}")
    except Exception as e:
        print(f"   请求失败: {e}")

if __name__ == "__main__":
    test_style_update() 