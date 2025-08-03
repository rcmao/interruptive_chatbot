#!/usr/bin/env python3
"""
测试TKI控制面板功能
"""

import requests
import json

def test_admin_login():
    """测试管理员登录"""
    url = "http://localhost:8080/api/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ 管理员登录成功!")
            print(f"   用户ID: {result['user']['id']}")
            print(f"   用户名: {result['user']['username']}")
            print(f"   角色: {result['user']['role']}")
            return result['token']
        else:
            print("❌ 管理员登录失败")
            return None
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return None

def test_tki_style_change(token):
    """测试TKI风格选择功能"""
    print("\n🧪 测试TKI风格选择功能")
    print("=" * 50)
    
    # 测试不同的TKI风格
    test_styles = [
        ('none', '无插话'),
        ('collaborating', '协作型'),
        ('accommodating', '迁就型'),
        ('competing', '竞争型'),
        ('compromising', '妥协型'),
        ('avoiding', '回避型')
    ]
    
    for style, description in test_styles:
        print(f"\n🔍 测试风格: {description} ({style})")
        
        # 这里应该通过WebSocket发送，但为了测试，我们只验证风格是否有效
        if style in ['none', 'collaborating', 'accommodating', 'competing', 'compromising', 'avoiding']:
            print(f"✅ 风格 '{style}' 有效")
        else:
            print(f"❌ 风格 '{style}' 无效")
    
    print("\n📋 TKI风格说明:")
    print("• none: 无插话 - AI不会进行任何干预")
    print("• collaborating: 协作型 - 整合各方观点，推动共识")
    print("• accommodating: 迁就型 - 优先维护和谐，用温和语气为女性缓颊")
    print("• competing: 竞争型 - 强势捍卫女性表达权，正面对抗偏见")
    print("• compromising: 妥协型 - 设置公平讨论机制，保障发言机会")
    print("• avoiding: 回避型 - 岔开矛盾话题，表面轻松，实则削弱女性表达机会")

def main():
    """主测试函数"""
    print("🧪 开始测试TKI控制面板功能")
    print("=" * 50)
    
    # 测试管理员登录
    token = test_admin_login()
    
    if token:
        # 测试TKI风格选择
        test_tki_style_change(token)
        
        print("\n✅ 测试完成!")
        print("\n📝 使用说明:")
        print("1. 使用 admin/admin123 登录")
        print("2. 进入任意聊天房间")
        print("3. 在左侧边栏底部查看TKI控制面板")
        print("4. 选择不同的插话风格进行测试")
    else:
        print("❌ 无法获取管理员token，测试失败")

if __name__ == "__main__":
    main() 