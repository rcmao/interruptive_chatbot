#!/usr/bin/env python3
"""
前端调试脚本 - 检查前端可能的问题
"""

import requests
import json

def debug_frontend():
    """调试前端问题"""
    base_url = "http://localhost:8080"
    
    print("=== 前端调试 ===")
    
    # 检查1：主页是否正常加载
    print("\n1. 检查主页")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 主页正常加载")
            # 检查是否包含必要的JavaScript
            if "localStorage" in response.text and "token" in response.text:
                print("✅ 主页包含token处理代码")
            else:
                print("❌ 主页缺少token处理代码")
        else:
            print(f"❌ 主页加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页访问错误: {e}")
    
    # 检查2：rooms页面是否正常加载
    print("\n2. 检查rooms页面")
    try:
        response = requests.get(f"{base_url}/rooms", timeout=5)
        if response.status_code == 200:
            print("✅ rooms页面正常加载")
            # 检查是否包含必要的JavaScript
            if "joinRoom" in response.text and "localStorage" in response.text:
                print("✅ rooms页面包含加入房间功能")
            else:
                print("❌ rooms页面缺少加入房间功能")
        else:
            print(f"❌ rooms页面加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ rooms页面访问错误: {e}")
    
    # 检查3：用户登录页面
    print("\n3. 检查登录页面")
    try:
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ 注册页面正常加载")
            if "login" in response.text.lower() or "register" in response.text.lower():
                print("✅ 注册页面包含登录功能")
            else:
                print("❌ 注册页面缺少登录功能")
        else:
            print(f"❌ 注册页面加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 注册页面访问错误: {e}")
    
    # 检查4：测试用户登录流程
    print("\n4. 测试用户登录流程")
    try:
        # 先尝试登录
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/api/login", json=login_data, timeout=5)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get('token')
            print(f"✅ 用户登录成功，token: {token[:20]}...")
            
            # 测试获取用户信息
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{base_url}/api/user/info", headers=headers, timeout=5)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ 获取用户信息成功: {user_info.get('username')}")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
        else:
            print(f"❌ 用户登录失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户登录流程错误: {e}")
    
    # 检查5：测试房间API
    print("\n5. 测试房间API")
    try:
        response = requests.get(f"{base_url}/api/rooms", timeout=5)
        if response.status_code == 200:
            rooms = response.json()
            print(f"✅ 获取房间列表成功，房间数量: {len(rooms)}")
            if rooms:
                room_id = rooms[0]['id']
                print(f"   第一个房间: {rooms[0].get('name')} (ID: {room_id})")
            else:
                print("   没有房间")
        else:
            print(f"❌ 获取房间列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 房间API错误: {e}")
    
    print("\n=== 前端调试完成 ===")
    print("\n建议检查:")
    print("1. 浏览器控制台是否有JavaScript错误")
    print("2. 网络请求是否正常发送")
    print("3. localStorage中的token是否正确设置")
    print("4. 用户是否已正确登录")

if __name__ == "__main__":
    debug_frontend() 