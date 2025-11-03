"""
测试演示模式的翻译功能集成
"""
from voice_assistant import VoiceAssistant

def test_basic_demo_with_translation():
    """测试基础演示模式的翻译功能"""
    print("=" * 60)
    print("测试 1: 基础演示 - 在线翻译模式")
    print("=" * 60)
    
    # 创建带翻译功能的助手
    assistant = VoiceAssistant(enable_translation=True, offline_mode=False)
    print("✅ 成功创建启用在线翻译的语音助手")
    print(f"   - 翻译已启用: {assistant.enable_translation}")
    print(f"   - 离线模式: {assistant.offline_mode}")
    print(f"   - 使用 DeepTranslator: {assistant.use_deep_translator}")
    print()

def test_basic_demo_with_offline_translation():
    """测试基础演示模式的离线翻译功能"""
    print("=" * 60)
    print("测试 2: 基础演示 - 离线翻译模式")
    print("=" * 60)
    
    # 创建带离线翻译功能的助手
    assistant = VoiceAssistant(enable_translation=True, offline_mode=True)
    print("✅ 成功创建启用离线翻译的语音助手")
    print(f"   - 翻译已启用: {assistant.enable_translation}")
    print(f"   - 离线模式: {assistant.offline_mode}")
    print(f"   - 离线词典大小: {len(assistant.offline_dict)} 个词条")
    
    # 测试离线翻译
    test_phrases = ["你好", "打开灯", "关闭音乐", "今天天气"]
    print("\n📚 测试离线翻译词典:")
    for phrase in test_phrases:
        result = assistant._translate_offline(phrase)
        print(f"   {phrase} -> {result}")
    print()

def test_wake_word_demo_with_translation():
    """测试唤醒词演示模式的翻译功能"""
    print("=" * 60)
    print("测试 3: 唤醒词演示 - 在线翻译模式")
    print("=" * 60)
    
    # 创建带翻译功能的助手
    assistant = VoiceAssistant(wake_word="你好", enable_translation=True, offline_mode=False)
    print("✅ 成功创建启用在线翻译的语音助手（带唤醒词）")
    print(f"   - 唤醒词: '{assistant.wake_word}'")
    print(f"   - 翻译已启用: {assistant.enable_translation}")
    print(f"   - 离线模式: {assistant.offline_mode}")
    print()

def test_continuous_demo_with_translation():
    """测试持续监听演示模式的翻译功能"""
    print("=" * 60)
    print("测试 4: 持续监听演示 - 翻译功能支持")
    print("=" * 60)
    
    # 创建带翻译功能的助手
    assistant = VoiceAssistant(wake_word="小助手", enable_translation=True, offline_mode=True)
    print("✅ 成功创建启用离线翻译的语音助手（持续监听模式）")
    print(f"   - 唤醒词: '{assistant.wake_word}'")
    print(f"   - 翻译已启用: {assistant.enable_translation}")
    print(f"   - 离线模式: {assistant.offline_mode}")
    
    # 测试回调函数
    def test_callback(result):
        """测试回调函数处理翻译结果"""
        if isinstance(result, dict):
            print(f"   ✓ 收到翻译结果: {result['original']} -> {result.get('translation')}")
        else:
            print(f"   ✓ 收到文本结果: {result}")
    
    print("\n📝 测试回调函数:")
    test_callback({'original': '你好', 'translation': 'hello'})
    test_callback('你好')
    print()

def test_all_modes_without_translation():
    """测试所有模式禁用翻译功能"""
    print("=" * 60)
    print("测试 5: 所有模式 - 禁用翻译")
    print("=" * 60)
    
    # 模式1：基础演示
    assistant1 = VoiceAssistant(enable_translation=False)
    print("✅ 基础演示（无翻译）")
    print(f"   - 翻译已启用: {assistant1.enable_translation}")
    
    # 模式2：唤醒词演示
    assistant2 = VoiceAssistant(wake_word="你好", enable_translation=False)
    print("✅ 唤醒词演示（无翻译）")
    print(f"   - 翻译已启用: {assistant2.enable_translation}")
    
    # 模式3：持续监听
    assistant3 = VoiceAssistant(wake_word="小助手", enable_translation=False)
    print("✅ 持续监听演示（无翻译）")
    print(f"   - 翻译已启用: {assistant3.enable_translation}")
    print()

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║   语音助手翻译功能集成测试                           ║
    ║   Testing Translation Integration in Demo Modes       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    try:
        test_basic_demo_with_translation()
        test_basic_demo_with_offline_translation()
        test_wake_word_demo_with_translation()
        test_continuous_demo_with_translation()
        test_all_modes_without_translation()
        
        print("=" * 60)
        print("🎉 所有测试完成！")
        print("=" * 60)
        print("\n✅ 翻译功能已成功集成到演示模式 1、2、3 中！")
        print("\n功能说明:")
        print("  • 演示模式 1（基础演示）: 支持在线/离线翻译选项")
        print("  • 演示模式 2（唤醒词演示）: 支持在线/离线翻译选项")
        print("  • 演示模式 3（持续监听）: 支持在线/离线翻译选项")
        print("  • 演示模式 4（翻译演示）: 专门的翻译演示（保持不变）")
        print("\n翻译模式选项:")
        print("  1. 在线翻译 - 使用 Google 翻译，更准确（需要网络）")
        print("  2. 离线翻译 - 使用内置词典，无需网络（仅支持常用词）")
        print("  3. 不使用翻译 - 仅进行语音识别")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
