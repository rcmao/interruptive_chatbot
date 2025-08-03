#!/usr/bin/env python3
"""
测试消息发送和接收功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_message_send():
    """测试消息发送功能"""
    
    print("测试消息发送功能...")
    
    # 1. 发送测试消息
    print("\n1. 发送测试消息...")
    try:
        message_data = {
            "room_id": 1,
            "content": "这是一条测试消息",
            "author": "测试用户"
        }
        
        response = requests.post(
            f"{BASE_URL}/test_send_message",
            json=message_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   消息发送成功: {result}")
        else:
            print(f"   消息发送失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 2. 等待一下让消息广播
    print("\n2. 等待消息广播...")
    time.sleep(2)
    
    # 3. 再次发送一条消息
    print("\n3. 发送第二条测试消息...")
    try:
        message_data = {
            "room_id": 1,
            "content": "这是第二条测试消息",
            "author": "另一个用户"
        }
        
        response = requests.post(
            f"{BASE_URL}/test_send_message",
            json=message_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   消息发送成功: {result}")
        else:
            print(f"   消息发送失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")

def test_websocket_broadcast():
    """测试WebSocket广播功能"""
    
    print("\n测试WebSocket广播功能...")
    
    # 这里可以添加WebSocket客户端测试
    # 由于需要实时连接，建议在浏览器中测试
    print("WebSocket测试需要在浏览器中进行")
    print("请打开聊天界面并发送消息来测试实时功能")

if __name__ == "__main__":
    test_message_send()
    test_websocket_broadcast() 