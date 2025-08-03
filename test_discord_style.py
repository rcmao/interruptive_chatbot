#!/usr/bin/env python3
import requests
import json

# 测试Discord风格聊天界面
def test_discord_style():
    base_url = "http://localhost:8080"
    
    # 1. 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🔐 正在登录...")
    login_response = requests.post(f"{base_url}/api/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result['token']
    print("✅ 登录成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取房间列表
    print("\n📋 获取房间列表...")
    rooms_response = requests.get(f"{base_url}/api/rooms", headers=headers)
    
    if rooms_response.status_code != 200:
        print(f"❌ 获取房间列表失败: {rooms_response.text}")
        return
    
    rooms = rooms_response.json()
    print(f"✅ 找到 {len(rooms)} 个房间")
    
    if len(rooms) == 0:
        print("❌ 没有房间可以测试")
        return
    
    # 选择第一个房间进行测试
    test_room = rooms[0]
    room_id = test_room['id']
    print(f"🎯 测试房间: {test_room['name']} (ID: {room_id})")
    
    # 3. 发送测试消息
    print("\n💬 发送测试消息...")
    message_data = {
        "content": "这是一个Discord风格的聊天界面测试消息！"
    }
    
    message_response = requests.post(
        f"{base_url}/api/rooms/{room_id}/messages",
        json=message_data,
        headers=headers
    )
    
    if message_response.status_code == 201:
        print("✅ 消息发送成功!")
        message_result = message_response.json()
        print(f"📝 消息内容: {message_result['content']}")
        print(f"👤 发送者: {message_result['author']}")
    else:
        print(f"❌ 消息发送失败: {message_response.text}")
    
    print("\n🌐 Discord风格聊天界面功能:")
    print(f"   访问地址: {base_url}/chat/{room_id}")
    print("   🎨 界面特色:")
    print("   - Discord风格的深色主题")
    print("   - 频道名称显示为 #general 格式")
    print("   - 顶部搜索栏和功能按钮")
    print("   - 消息输入区域包含附件、GIF、表情等按钮")
    print("   - 右侧成员列表显示在线/离线状态")
    print("   - 可切换成员列表显示/隐藏")
    print("   - 实时消息发送和接收")

if __name__ == "__main__":
    test_discord_style() 