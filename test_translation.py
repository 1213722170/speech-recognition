"""
翻译功能测试脚本
用于验证 deep-translator 是否正常工作
"""

print("=" * 60)
print("翻译功能测试")
print("=" * 60)

# 测试 deep_translator
try:
    from deep_translator import GoogleTranslator
    print("✅ deep-translator 已成功安装")
    
    # 测试翻译
    test_text = "你好世界"
    print(f"\n🔤 测试文本: {test_text}")
    
    translator = GoogleTranslator(source='auto', target='en')
    result = translator.translate(test_text)
    
    print(f"✅ 翻译成功: {result}")
    print("\n🎉 deep-translator 工作正常，不会有SSL错误！")
    
except ImportError:
    print("❌ deep-translator 未安装")
    print("💡 请运行: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple deep-translator")
except Exception as e:
    print(f"❌ 翻译测试失败: {e}")

print("\n" + "=" * 60)

# 测试 googletrans（可选）
try:
    from googletrans import Translator
    print("✅ googletrans 已安装（备用方案）")
except ImportError:
    print("⚠️ googletrans 未安装（不影响使用）")

print("=" * 60)
print("\n💡 提示: 现在可以运行 voice_assistant.py 使用稳定的翻译功能！")
print("📝 命令: python voice_assistant.py")
print("=" * 60)
