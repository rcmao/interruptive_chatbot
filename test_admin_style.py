#!/usr/bin/env python3
"""
测试admin页面的风格切换功能
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def create_admin_user():
    """创建管理员用户"""
    print("创建管理员用户...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/register",
            json={
                "username": "admin_test",
                "email": "admin@test.com",
                "password": "admin123",
                "role": "admin"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("管理员用户创建成功")
            return True
        else:
            print(f"创建用户失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"创建用户请求失败: {e}")
        return False

def login_admin():
    """登录管理员用户"""
    print("登录管理员用户...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={
                "username": "admin_test",
                "password": "admin123"
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            if token:
                print("登录成功")
                return token
            else:
                print("登录失败：未获取到token")
                return None
        else:
            print(f"登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"登录请求失败: {e}")
        return None

def test_style_management():
    """测试风格管理功能"""
    
    print("=== 测试Admin页面风格切换功能 ===")
    
    # 创建管理员用户
    create_admin_user()
    
    # 登录获取token
    token = login_admin()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 1. 获取当前风格
    print("\n1. 获取当前风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"当前风格: {data.get('style', 'unknown')}")
        else:
            print(f"获取当前风格失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试更新风格为协作型
    print("\n2. 测试更新风格为协作型...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/intervention-style",
            json={"style": "collaborating"},
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"更新结果: {data}")
        else:
            print(f"更新失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 再次获取当前风格确认更新
    print("\n3. 确认风格更新...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"更新后风格: {data.get('style', 'unknown')}")
        else:
            print(f"获取当前风格失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试更新风格为无插话
    print("\n4. 测试更新风格为无插话...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/intervention-style",
            json={"style": "none"},
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"更新结果: {data}")
        else:
            print(f"更新失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 5. 最终确认
    print("\n5. 最终确认风格...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/current-intervention-style", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"最终风格: {data.get('style', 'unknown')}")
        else:
            print(f"获取当前风格失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == '__main__':
    test_style_management() 