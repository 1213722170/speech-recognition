"""
翻译问题诊断和修复工具
自动检测并修复代理/SSL相关的翻译错误
"""
import os
import sys

print("=" * 70)
print("🔧 翻译问题诊断和修复工具")
print("=" * 70)

# 1. 检查代理设置
print("\n📡 步骤 1: 检查代理设置...")
proxy_found = False
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']

for var in proxy_vars:
    if var in os.environ:
        print(f"   ⚠️ 发现代理设置: {var} = {os.environ[var]}")
        proxy_found = True

if proxy_found:
    print("\n   💡 代理设置可能导致翻译SSL错误")
    choice = input("\n   是否临时清除代理设置? (y/n): ").strip().lower()
    if choice == 'y':
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
                print(f"   ✅ 已清除: {var}")
        print("\n   ✅ 代理已临时清除（仅本次运行有效）")
else:
    print("   ✅ 未发现代理设置")

# 2. 检查翻译库
print("\n📦 步骤 2: 检查翻译库安装...")

# 检查 deep-translator
try:
    from deep_translator import GoogleTranslator
    print("   ✅ deep-translator 已安装（推荐）")
    deep_available = True
except ImportError:
    print("   ❌ deep-translator 未安装")
    deep_available = False

# 检查 googletrans
try:
    from googletrans import Translator
    print("   ✅ googletrans 已安装（备选）")
    google_available = True
except ImportError:
    print("   ❌ googletrans 未安装")
    google_available = False

# 3. 安装建议
if not deep_available:
    print("\n💡 步骤 3: 安装推荐")
    print("\n   强烈推荐安装 deep-translator（更稳定，无SSL问题）:")
    print("\n   方法1 - 使用国内镜像源（推荐）:")
    print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple deep-translator")
    print("\n   方法2 - 使用默认源:")
    print("   pip install deep-translator")
    
    choice = input("\n   是否现在安装? (y/n): ").strip().lower()
    if choice == 'y':
        import subprocess
        print("\n   正在安装 deep-translator...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-i", 
                 "https://pypi.tuna.tsinghua.edu.cn/simple", "deep-translator"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("   ✅ 安装成功!")
                deep_available = True
            else:
                print(f"   ❌ 安装失败: {result.stderr}")
        except Exception as e:
            print(f"   ❌ 安装失败: {e}")

# 4. 测试翻译功能
if deep_available or google_available:
    print("\n🧪 步骤 4: 测试翻译功能...")
    
    test_text = "你好世界"
    print(f"\n   测试文本: {test_text}")
    
    # 测试 deep-translator
    if deep_available:
        try:
            print("\n   🌐 使用 deep-translator 测试...")
            # 清除代理
            for var in proxy_vars:
                if var in os.environ:
                    del os.environ[var]
            
            translator = GoogleTranslator(source='auto', target='en')
            result = translator.translate(test_text)
            print(f"   ✅ 翻译成功: {result}")
            print("\n   🎉 deep-translator 工作正常!")
        except Exception as e:
            print(f"   ❌ 翻译失败: {type(e).__name__}")
            print(f"   详细: {str(e)[:100]}")
    
    # 测试 googletrans
    elif google_available:
        try:
            print("\n   🌐 使用 googletrans 测试...")
            # 清除代理
            for var in proxy_vars:
                if var in os.environ:
                    del os.environ[var]
            
            translator = Translator()
            result = translator.translate(test_text, src='auto', dest='en')
            print(f"   ✅ 翻译成功: {result.text}")
            print("\n   ⚠️ googletrans 可用，但建议升级到 deep-translator")
        except Exception as e:
            print(f"   ❌ 翻译失败: {type(e).__name__}")
            print(f"   详细: {str(e)[:100]}")
            print("\n   💡 建议安装 deep-translator 以获得更好的稳定性")

# 5. 总结和建议
print("\n" + "=" * 70)
print("📋 诊断总结")
print("=" * 70)

if deep_available:
    print("\n✅ 状态: 良好")
    print("   - deep-translator 已安装并可用")
    print("   - 程序会自动使用最稳定的翻译引擎")
    print("\n🚀 可以直接运行: python voice_assistant.py")
elif google_available:
    print("\n⚠️ 状态: 可用但不推荐")
    print("   - 仅安装了 googletrans（可能有SSL问题）")
    print("   - 建议安装 deep-translator 以获得更好的稳定性")
    print("\n💡 安装命令:")
    print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple deep-translator")
else:
    print("\n❌ 状态: 需要安装翻译库")
    print("   - 未安装任何翻译库")
    print("\n💡 安装命令:")
    print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple deep-translator")

print("\n" + "=" * 70)

# 6. 创建快捷脚本
print("\n💾 步骤 5: 创建便捷启动脚本...")

# Windows批处理脚本
bat_content = """@echo off
echo 正在启动语音助手（已禁用代理）...
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
python voice_assistant.py
pause
"""

try:
    with open("start_assistant.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    print("   ✅ 已创建: start_assistant.bat")
    print("   💡 双击此文件可直接启动（自动禁用代理）")
except Exception as e:
    print(f"   ⚠️ 创建启动脚本失败: {e}")

print("\n" + "=" * 70)
print("✅ 诊断完成!")
print("=" * 70)
