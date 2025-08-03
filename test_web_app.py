#!/usr/bin/env python3
"""
Web应用测试脚本 - 测试所有Web功能是否正常工作
"""

import requests
import json
import time

def test_web_app():
    """测试Web应用功能"""
    base_url = "http://localhost:8080"
    
    print("=== Web应用功能测试 ===")
    
    # 测试1：主页访问
    print("\n1. 测试主页访问")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 主页访问正常")
        else:
            print(f"❌ 主页访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页访问错误: {e}")
    
    # 测试2：注册页面
    print("\n2. 测试注册页面")
    try:
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ 注册页面访问正常")
        else:
            print(f"❌ 注册页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 注册页面访问错误: {e}")
    
    # 测试3：语言API
    print("\n3. 测试语言API")
    try:
        response = requests.get(f"{base_url}/api/language", timeout=5)
        if response.status_code == 200:
            languages = response.json()
            print(f"✅ 语言API正常，支持语言: {languages}")
        else:
            print(f"❌ 语言API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 语言API错误: {e}")
    
    # 测试4：翻译API
    print("\n4. 测试翻译API")
    try:
        response = requests.get(f"{base_url}/api/translations/zh", timeout=5)
        if response.status_code == 200:
            translations = response.json()
            print(f"✅ 翻译API正常，翻译数量: {len(translations)}")
        else:
            print(f"❌ 翻译API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 翻译API错误: {e}")
    
    # 测试5：Admin风格API（需要权限）
    print("\n5. 测试Admin风格API")
    try:
        response = requests.get(f"{base_url}/api/admin/current-intervention-style", timeout=5)
        if response.status_code == 200:
            style_data = response.json()
            print(f"✅ Admin风格API正常，当前风格: {style_data.get('style', 'unknown')}")
        elif response.status_code == 401 or response.status_code == 403:
            print("✅ Admin风格API权限检查正常（需要管理员权限）")
        else:
            print(f"❌ Admin风格API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin风格API错误: {e}")
    
    # 测试6：检测状态API（需要权限）
    print("\n6. 测试检测状态API")
    try:
        response = requests.get(f"{base_url}/api/admin/detection-status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ 检测状态API正常，状态: {status_data.get('status', 'unknown')}")
        elif response.status_code == 401 or response.status_code == 403:
            print("✅ 检测状态API权限检查正常（需要管理员权限）")
        else:
            print(f"❌ 检测状态API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 检测状态API错误: {e}")
    
    # 测试7：测试广播API
    print("\n7. 测试广播API")
    try:
        response = requests.get(f"{base_url}/test_broadcast", timeout=5)
        if response.status_code == 200:
            broadcast_data = response.json()
            print(f"✅ 广播API正常: {broadcast_data.get('message', 'unknown')}")
        else:
            print(f"❌ 广播API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 广播API错误: {e}")
    
    print("\n=== Web应用测试完成 ===")

if __name__ == "__main__":
    test_web_app() 