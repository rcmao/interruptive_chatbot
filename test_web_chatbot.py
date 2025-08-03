#!/usr/bin/env python3
"""
测试Web应用中的chatbot插话功能
"""

import requests
import json
import time
from datetime import datetime

# Web应用的基础URL
BASE_URL = "http://localhost:8080"

def test_web_chatbot():
    """测试Web应用中的chatbot插话功能"""
    
    print("🧪 开始测试Web应用中的chatbot插话功能...")
    print("=" * 60)
    
    # 1. 注册测试用户
    print("1. 注册测试用户...")
    users = []
    
    # 注册女性用户
    female_user = {
        "username": "test_lily",
        "email": "lily@test.com", 
        "password": "test123",
        "gender": "female"
    }
    
    # 注册男性用户
    male_user = {
        "username": "test_alex",
        "email": "alex@test.com",
        "password": "test123", 
        "gender": "male"
    }
    
    for user_data in [female_user, male_user]:
        try:
            response = requests.post(f"{BASE_URL}/api/register", json=user_data)
            if response.status_code == 200:
                print(f"✅ 用户 {user_data['username']} 注册成功")
                users.append(user_data)
            else:
                print(f"⚠️ 用户 {user_data['username']} 可能已存在")
                users.append(user_data)
        except Exception as e:
            print(f"❌ 注册用户失败: {e}")
            return
    
    # 2. 登录用户
    print("\n2. 登录用户...")
    sessions = []
    
    for user in users:
        try:
            login_data = {
                "username": user["username"],  # 使用username而不是email
                "password": user["password"]
            }
            response = requests.post(f"{BASE_URL}/api/login", json=login_data)
            if response.status_code == 200:
                session_token = response.cookies.get('session')
                print(f"✅ 用户 {user['username']} 登录成功")
                sessions.append({
                    "user": user,
                    "cookies": {"session": session_token}
                })
            else:
                print(f"❌ 用户 {user['username']} 登录失败: {response.text}")
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return
    
    # 3. 创建聊天房间
    print("\n3. 创建聊天房间...")
    try:
        room_data = {
            "name": "测试房间",
            "description": "用于测试chatbot插话功能",
            "max_members": 10,
            "is_private": False,
            "tki_style": "collaborating"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/rooms", 
            json=room_data,
            cookies=sessions[0]["cookies"]
        )
        
        if response.status_code == 200:
            room_info = response.json()
            room_id = room_info.get("id")
            print(f"✅ 房间创建成功，ID: {room_id}")
        else:
            print(f"❌ 房间创建失败: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 创建房间失败: {e}")
        return
    
    # 4. 加入房间
    print("\n4. 用户加入房间...")
    for session in sessions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/rooms/{room_id}/join",
                cookies=session["cookies"]
            )
            if response.status_code == 200:
                print(f"✅ 用户 {session['user']['username']} 加入房间成功")
            else:
                print(f"❌ 用户 {session['user']['username']} 加入房间失败")
        except Exception as e:
            print(f"❌ 加入房间失败: {e}")
    
    # 5. 发送测试消息
    print("\n5. 发送测试消息...")
    
    # 模拟对话场景：女性被打断
    test_scenarios = [
        {
            "user": sessions[0],  # 女性用户
            "message": "我觉得这个问题可以从另一个角度来考虑...",
            "description": "女性开始表达观点"
        },
        {
            "user": sessions[1],  # 男性用户
            "message": "不对，你说得不对，应该是这样...",
            "description": "男性打断女性"
        },
        {
            "user": sessions[1],  # 男性用户
            "message": "而且我觉得你的想法太简单了",
            "description": "男性继续主导对话"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        try:
            message_data = {
                "content": scenario["message"],
                "room_id": room_id
            }
            
            response = requests.post(
                f"{BASE_URL}/api/rooms/{room_id}/messages",
                json=message_data,
                cookies=scenario["user"]["cookies"]
            )
            
            if response.status_code == 200:
                print(f"✅ 消息 {i} 发送成功: {scenario['description']}")
                print(f"   内容: {scenario['message']}")
                print(f"   发送者: {scenario['user']['user']['username']}")
            else:
                print(f"❌ 消息 {i} 发送失败: {response.text}")
                
            # 等待一下，让系统处理消息
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
    
    # 6. 检查干预记录
    print("\n6. 检查干预记录...")
    try:
        # 获取房间消息
        response = requests.get(
            f"{BASE_URL}/api/rooms/{room_id}/messages",
            cookies=sessions[0]["cookies"]
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ 获取到 {len(messages)} 条消息")
            
            # 检查是否有干预消息
            interventions = [msg for msg in messages if msg.get("has_interruption")]
            if interventions:
                print(f"🎯 发现 {len(interventions)} 条干预消息:")
                for intervention in interventions:
                    print(f"   - 策略: {intervention.get('interruption_type')}")
                    print(f"   - 内容: {intervention.get('content', 'N/A')}")
            else:
                print("⚠️ 没有发现干预消息")
                
        else:
            print(f"❌ 获取消息失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 检查干预记录失败: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 测试完成！")
    print(f"📝 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 提示: 如果看到干预消息，说明chatbot插话功能正常工作")

if __name__ == "__main__":
    test_web_chatbot() 