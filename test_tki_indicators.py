#!/usr/bin/env python3
"""
测试TKI风格指示器的颜色映射
"""

def test_tki_color_mapping():
    """测试TKI风格颜色映射"""
    
    # TKI风格颜色映射
    tki_colors = {
        'none': '#747f8d',           # 灰色
        'collaborating': '#5865f2',   # 蓝色
        'accommodating': '#57f287',   # 绿色
        'competing': '#ed4245',       # 红色
        'compromising': '#faa61a',    # 橙色
        'avoiding': '#eb459e'         # 粉色
    }
    
    # TKI风格描述
    tki_descriptions = {
        'none': '无插话 - AI不会进行任何干预',
        'collaborating': '协作型 - 整合各方观点，推动共识，平衡支持女性表达与维护群体和谐',
        'accommodating': '迁就型 - 优先维护和谐，用温和语气为女性缓颊，避免冲突',
        'competing': '竞争型 - 强势捍卫女性表达权，正面对抗偏见，可能激化冲突',
        'compromising': '妥协型 - 设置公平讨论机制，保障发言机会，不参与观点评价',
        'avoiding': '回避型 - 岔开矛盾话题，表面轻松，实则削弱女性表达机会'
    }
    
    # TKI风格显示名称
    tki_display_names = {
        'none': '无插话',
        'collaborating': '协作型',
        'accommodating': '迁就型',
        'competing': '竞争型',
        'compromising': '妥协型',
        'avoiding': '回避型'
    }
    
    print("🎨 TKI风格指示器颜色映射测试")
    print("=" * 50)
    
    for style, color in tki_colors.items():
        print(f"📊 {tki_display_names[style]}")
        print(f"   颜色代码: {color}")
        print(f"   描述: {tki_descriptions[style]}")
        print(f"   CSS类名: tki-style-{style}")
        print()
    
    print("✅ 颜色映射测试完成！")
    print("\n📝 使用说明:")
    print("1. 管理员可以在聊天室侧边栏看到TKI控制面板")
    print("2. 普通用户可以在聊天头部看到TKI状态指示器")
    print("3. 不同颜色代表不同的TKI干预策略")
    print("4. 颜色会实时同步到所有用户界面")

if __name__ == '__main__':
    test_tki_color_mapping() 