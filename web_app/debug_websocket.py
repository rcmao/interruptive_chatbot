#!/usr/bin/env python3
"""
调试WebSocket事件处理
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_websocket_events():
    """测试WebSocket事件处理"""
    
    print("调试WebSocket事件处理...")
    
    # 1. 测试直接发送WebSocket消息
    print("\n1. 测试WebSocket消息发送...")
    try:
        # 使用requests发送WebSocket消息（模拟）
        message_data = {
            "room": "1",
            "message": {
                "content": "WebSocket测试消息",
                "gender": "unknown"
            }
        }
        
        # 这里我们需要一个真实的WebSocket客户端来测试
        print("   注意：需要真实的WebSocket客户端来测试")
        print("   请使用浏览器访问测试页面进行测试")
        
    except Exception as e:
        print(f"   测试失败: {e}")
    
    # 2. 检查服务器状态
    print("\n2. 检查服务器状态...")
    try:
        response = requests.get(f"{BASE_URL}/test_broadcast")
        if response.status_code == 200:
            print("   服务器运行正常")
        else:
            print(f"   服务器状态异常: {response.status_code}")
    except Exception as e:
        print(f"   无法连接到服务器: {e}")

def check_server_logs():
    """检查服务器日志"""
    print("\n3. 检查服务器日志...")
    print("   请查看运行Flask应用的终端窗口")
    print("   应该能看到类似以下的日志：")
    print("   - 收到WebSocket消息: {...}")
    print("   - 房间: 1, 消息数据: {...}")
    print("   - 用户ID: ...")
    print("   - 用户信息: ...")
    print("   - 创建消息: ...")
    print("   - 消息已保存到数据库，ID: ...")
    print("   - 准备广播消息: {...}")
    print("   - 消息已广播到房间 1")
    print("   - 消息已向所有客户端广播")

if __name__ == "__main__":
    test_websocket_events()
    check_server_logs() 