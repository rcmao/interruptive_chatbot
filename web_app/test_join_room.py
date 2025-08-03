#!/usr/bin/env python3
"""
测试加入房间功能的脚本
"""
import requests
import json
import sqlite3
import os

# 配置
BASE_URL = "http://localhost:8080"
DB_PATH = "instance/chatbot.db"

def check_database():
    """检查数据库状态"""
    print("=== 检查数据库 ===")
    if not os.path.exists(DB_PATH):
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ 数据库表: {[table[0] for table in tables]}")
        
        # 检查用户
        cursor.execute("SELECT id, username, role FROM user LIMIT 5;")
        users = cursor.fetchall()
        print(f"✅ 用户数量: {len(users)}")
        for user in users:
            print(f"   - ID: {user[0]}, 用户名: {user[1]}, 角色: {user[2]}")
        
        # 检查房间
        cursor.execute("SELECT id, name, created_by FROM room LIMIT 5;")
        rooms = cursor.fetchall()
        print(f"✅ 房间数量: {len(rooms)}")
        for room in rooms:
            print(f"   - ID: {room[0]}, 名称: {room[1]}, 创建者: {room[2]}")
        
        # 检查房间成员
        cursor.execute("SELECT user_id, room_id FROM room_membership LIMIT 5;")
        memberships = cursor.fetchall()
        print(f"✅ 房间成员关系数量: {len(memberships)}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def test_login():
    """测试登录功能"""
    print("\n=== 测试登录 ===")
    
    # 尝试登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"登录响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ 登录成功，获得token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def test_join_room(token, room_id=1):
    """测试加入房间"""
    print(f"\n=== 测试加入房间 {room_id} ===")
    
    if not token:
        print("❌ 没有有效的token")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 先检查房间是否存在
        print("1. 检查房间是否存在...")
        response = requests.get(f"{BASE_URL}/api/rooms/{room_id}", headers=headers)
        print(f"   房间检查响应: {response.status_code}")
        
        if response.status_code == 200:
            room_data = response.json()
            print(f"   ✅ 房间存在: {room_data}")
        else:
            print(f"   ❌ 房间不存在: {response.text}")
            return False
        
        # 尝试加入房间
        print("2. 尝试加入房间...")
        response = requests.post(f"{BASE_URL}/api/rooms/{room_id}/join", headers=headers)
        print(f"   加入房间响应: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功加入房间: {data}")
            return True
        else:
            print(f"   ❌ 加入房间失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 加入房间请求失败: {e}")
        return False

def test_chat_room_access(room_id=1):
    """测试聊天房间页面访问"""
    print(f"\n=== 测试聊天房间页面访问 {room_id} ===")
    
    try:
        # 使用session来保持登录状态
        session = requests.Session()
        
        # 先登录获取session
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get('token')
            session.headers.update({'Authorization': f'Bearer {token}'})
        
        # 访问聊天房间页面
        response = session.get(f"{BASE_URL}/chat/{room_id}")
        print(f"聊天房间页面响应: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 聊天房间页面可以访问")
            return True
        else:
            print(f"❌ 聊天房间页面访问失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 聊天房间页面请求失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试加入房间功能...")
    
    # 检查数据库
    if not check_database():
        return
    
    # 测试登录
    token = test_login()
    
    # 测试加入房间
    if token:
        test_join_room(token)
    
    # 测试聊天房间页面访问
    test_chat_room_access()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 