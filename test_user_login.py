#!/usr/bin/env python3
"""
用户登录和加入房间测试脚本
"""

import requests
import json

def test_user_login_and_join():
    """测试用户登录和加入房间功能"""
    base_url = "http://localhost:8080"
    
    print("=== 用户登录和加入房间测试 ===")
    
    # 测试1：用户注册
    print("\n1. 测试用户注册")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "gender": "male"
    }
    
    try:
        response = requests.post(f"{base_url}/api/register", json=register_data, timeout=5)
        if response.status_code == 201:
            print("✅ 用户注册成功")
        elif response.status_code == 400 and "已存在" in response.text:
            print("✅ 用户已存在，继续测试")
        else:
            print(f"❌ 用户注册失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 用户注册错误: {e}")
    
    # 测试2：用户登录
    print("\n2. 测试用户登录")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/login", json=login_data, timeout=5)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get('token')
            print(f"✅ 用户登录成功，获得token: {token[:20]}...")
            
            # 保存token用于后续测试
            headers = {'Authorization': f'Bearer {token}'}
        else:
            print(f"❌ 用户登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 用户登录错误: {e}")
        return
    
    # 测试3：获取房间列表
    print("\n3. 测试获取房间列表")
    try:
        response = requests.get(f"{base_url}/api/rooms", timeout=5)
        if response.status_code == 200:
            rooms = response.json()
            print(f"✅ 获取房间列表成功，房间数量: {len(rooms)}")
            if rooms:
                room_id = rooms[0]['id']
                print(f"   第一个房间ID: {room_id}")
            else:
                print("   没有房间，创建测试房间")
                # 创建测试房间
                room_data = {
                    "name": "测试房间",
                    "description": "用于测试的房间",
                    "max_members": 10
                }
                response = requests.post(f"{base_url}/api/rooms", json=room_data, timeout=5)
                if response.status_code == 201:
                    room = response.json()
                    room_id = room['id']
                    print(f"✅ 创建测试房间成功，房间ID: {room_id}")
                else:
                    print(f"❌ 创建测试房间失败: {response.status_code}")
                    return
        else:
            print(f"❌ 获取房间列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 获取房间列表错误: {e}")
        return
    
    # 测试4：加入房间
    print(f"\n4. 测试加入房间 (房间ID: {room_id})")
    try:
        response = requests.post(f"{base_url}/api/rooms/{room_id}/join", headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 加入房间成功: {result.get('message', '成功')}")
        else:
            error = response.json()
            print(f"❌ 加入房间失败: {response.status_code} - {error.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 加入房间错误: {e}")
    
    # 测试5：获取房间信息
    print(f"\n5. 测试获取房间信息 (房间ID: {room_id})")
    try:
        response = requests.get(f"{base_url}/api/rooms/{room_id}", headers=headers, timeout=5)
        if response.status_code == 200:
            room_info = response.json()
            print(f"✅ 获取房间信息成功:")
            print(f"   房间名称: {room_info.get('name')}")
            print(f"   成员数量: {room_info.get('member_count')}")
            print(f"   最大成员: {room_info.get('max_members')}")
        else:
            error = response.json()
            print(f"❌ 获取房间信息失败: {response.status_code} - {error.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 获取房间信息错误: {e}")
    
    # 测试6：获取房间成员
    print(f"\n6. 测试获取房间成员 (房间ID: {room_id})")
    try:
        response = requests.get(f"{base_url}/api/rooms/{room_id}/members", headers=headers, timeout=5)
        if response.status_code == 200:
            members = response.json()
            print(f"✅ 获取房间成员成功，成员数量: {len(members)}")
            for member in members:
                print(f"   成员: {member.get('username')} ({member.get('gender')})")
        else:
            error = response.json()
            print(f"❌ 获取房间成员失败: {response.status_code} - {error.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 获取房间成员错误: {e}")
    
    print("\n=== 用户登录和加入房间测试完成 ===")

if __name__ == "__main__":
    test_user_login_and_join() 