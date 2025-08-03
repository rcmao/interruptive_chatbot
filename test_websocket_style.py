#!/usr/bin/env python3
"""
测试WebSocket实时风格更新功能
"""

import socketio
import time
import json

# 创建Socket.IO客户端
sio = socketio.Client()

@sio.event
def connect():
    print("✅ 已连接到WebSocket服务器")

@sio.event
def disconnect():
    print("❌ 与WebSocket服务器断开连接")

@sio.on('tki_style_updated')
def on_tki_style_updated(data):
    print(f"📡 收到TKI风格更新: {data}")

@sio.on('intervention_style_updated')
def on_intervention_style_updated(data):
    print(f"📡 收到干预风格更新: {data}")

def test_websocket_style_update():
    """测试WebSocket风格更新"""
    print("=== 测试WebSocket实时风格更新 ===")
    
    try:
        # 连接到WebSocket服务器
        print("\n1. 连接到WebSocket服务器...")
        sio.connect('http://localhost:8081')
        
        # 加入房间
        print("\n2. 加入房间...")
        sio.emit('join_room', {'room': '1'})
        time.sleep(1)
        
        # 发送风格更新事件
        print("\n3. 发送风格更新事件...")
        sio.emit('tki_style_change', {
            'room': '1',
            'style': 'competing'
        })
        
        # 等待接收更新
        print("\n4. 等待接收更新...")
        time.sleep(3)
        
        # 发送另一个风格更新
        print("\n5. 发送另一个风格更新...")
        sio.emit('tki_style_change', {
            'room': '1',
            'style': 'collaborating'
        })
        
        # 等待接收更新
        print("\n6. 等待接收更新...")
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 断开连接
        if sio.connected:
            sio.disconnect()
        print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_websocket_style_update() 