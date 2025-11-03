"""
测试离线翻译功能
"""
from voice_assistant import VoiceAssistant

print("=" * 60)
print("🧪 测试离线翻译功能")
print("=" * 60)

# 创建离线翻译助手
assistant = VoiceAssistant(enable_translation=True, offline_mode=True)

# 测试用例
test_cases = [
    "你好世界",
    "今天天气很好",
    "打开灯",
    "关闭空调",
    "早上好",
    "晚安",
    "谢谢",
    "再见",
]

print("\n测试离线翻译词典:\n")

for text in test_cases:
    print(f"原文: {text}")
    result = assistant.translate_to_english(text)
    print()

print("=" * 60)
print("✅ 测试完成!")
print("=" * 60)
print("\n💡 提示: 离线翻译模式无需网络，不受代理影响，始终可用！")
