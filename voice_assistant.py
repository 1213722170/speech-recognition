"""
语音助手 - 包含语音唤醒、语音捕获和语音识别功能
"""
import speech_recognition as sr
import pyaudio
import numpy as np
from collections import deque
import time
import threading
import urllib3
import ssl
import os

# 翻译库导入（支持多个备选方案）
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False
    print("⚠️ deep_translator 未安装，将使用 googletrans")

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("⚠️ googletrans 未安装")

# 导入 requests 用于禁用代理
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class VoiceAssistant:
    def __init__(self, wake_word="你好小助手", language="zh-CN", enable_translation=False, offline_mode=False):
        """
        初始化语音助手
        
        Args:
            wake_word: 唤醒词
            language: 识别语言，默认中文
            enable_translation: 是否启用翻译功能
            offline_mode: 是否使用离线翻译模式（使用简单词典）
        """
        self.wake_word = wake_word.lower()
        self.language = language
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.is_awake = False
        self.enable_translation = enable_translation
        self.offline_mode = offline_mode
        
        # 初始化翻译器
        if enable_translation:
            # 优先使用 deep_translator（更稳定）
            self.use_deep_translator = DEEP_TRANSLATOR_AVAILABLE and not offline_mode
            
            # 如果 deep_translator 不可用，使用 googletrans
            if not self.use_deep_translator and GOOGLETRANS_AVAILABLE and not offline_mode:
                self.translator = Translator(service_urls=['translate.google.com'])
            
            # 翻译重试次数
            self.max_translation_retries = 3
            self.translation_timeout = 5
            
            # 简单的离线翻译词典（备用方案）
            self._init_offline_dict()
        
        # 调整识别参数以提高准确性
        self.recognizer.energy_threshold = 4000  # 能量阈值
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5  # 语音暂停阈值(秒) - 增加到1.5秒，避免说话中途被打断
        self.recognizer.non_speaking_duration = 0.8  # 非语音持续时间(秒)
    
    def _init_offline_dict(self):
        """初始化离线翻译词典（简单的中英文对照）"""
        self.offline_dict = {
            # 常用词汇
            "你好": "hello",
            "世界": "world",
            "再见": "goodbye",
            "谢谢": "thank you",
            "是": "yes",
            "不": "no",
            "时间": "time",
            "天气": "weather",
            "今天": "today",
            "明天": "tomorrow",
            "昨天": "yesterday",
            "早上": "morning",
            "下午": "afternoon",
            "晚上": "evening",
            "晚安": "good night",
            "早安": "good morning",
            "帮助": "help",
            "打开": "open",
            "关闭": "close",
            "开始": "start",
            "停止": "stop",
            "音乐": "music",
            "灯": "light",
            "灯光": "light",
            "空调": "air conditioner",
            "电视": "television",
            "窗户": "window",
            "门": "door",
        }
        
    def listen_for_audio(self, timeout=5, phrase_time_limit=None):
        """
        捕获音频输入
        
        Args:
            timeout: 等待开始说话的超时时间(秒)
            phrase_time_limit: 单次录音的最大时长(秒)
            
        Returns:
            audio: 捕获的音频数据，如果失败返回None
        """
        try:
            with sr.Microphone() as source:
                print("🎤 正在调整环境噪音...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🎤 请说话...")
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                return audio
        except sr.WaitTimeoutError:
            print("⏱️ 等待超时，未检测到语音")
            return None
        except Exception as e:
            print(f"❌ 音频捕获错误: {e}")
            return None
    
    def recognize_speech(self, audio, show_all=False):
        """
        识别语音内容
        
        Args:
            audio: 音频数据
            show_all: 是否显示所有可能的识别结果
            
        Returns:
            str: 识别的文本，如果失败返回None
        """
        if audio is None:
            return None
            
        try:
            print("🔍 正在识别语音...")
            
            # 使用Google语音识别
            text = self.recognizer.recognize_google(
                audio, 
                language=self.language,
                show_all=show_all
            )
            
            if show_all and isinstance(text, dict):
                print(f"📝 所有识别结果: {text}")
                if text.get('alternative'):
                    return text['alternative'][0]['transcript']
                return None
            
            return text
            
        except sr.UnknownValueError:
            print("❓ 无法识别语音内容")
            return None
        except sr.RequestError as e:
            print(f"❌ 识别服务错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 识别错误: {e}")
            return None
    
    def translate_to_english(self, text):
        """
        将识别的文字翻译成英文（带重试机制和多种翻译引擎）
        
        Args:
            text: 要翻译的文本
            
        Returns:
            str: 翻译后的英文文本，如果失败返回None
        """
        if not text or not self.enable_translation:
            return None
        
        # 离线模式：使用简单词典
        if self.offline_mode:
            return self._translate_offline(text)
        
        # 优先使用 deep_translator（更稳定，无SSL问题）
        if self.use_deep_translator:
            result = self._translate_with_deep_translator(text)
            # 如果失败，降级到离线模式
            if result is None:
                print("💡 尝试使用离线翻译...")
                return self._translate_offline(text)
            return result
        
        # 备选方案：使用 googletrans
        if GOOGLETRANS_AVAILABLE:
            result = self._translate_with_googletrans(text)
            # 如果失败，降级到离线模式
            if result is None:
                print("💡 尝试使用离线翻译...")
                return self._translate_offline(text)
            return result
        
        # 没有在线翻译工具，使用离线模式
        print("⚠️ 没有可用的在线翻译引擎，使用离线模式")
        return self._translate_offline(text)
    
    def _translate_offline(self, text):
        """
        离线翻译（使用简单词典）
        """
        print("📚 使用离线词典翻译...")
        
        # 分词并翻译
        words = text.split()
        translated_words = []
        
        for word in words:
            # 查找完整匹配
            if word in self.offline_dict:
                translated_words.append(self.offline_dict[word])
            else:
                # 尝试部分匹配
                found = False
                for key, value in self.offline_dict.items():
                    if key in word:
                        translated_words.append(value)
                        found = True
                        break
                if not found:
                    # 保留原文
                    translated_words.append(word)
        
        result = " ".join(translated_words)
        
        if result == text:
            print("⚠️ 离线词典中未找到对应翻译")
            print("💡 提示: 请安装在线翻译库以获得更好的翻译效果")
            return None
        else:
            print(f"✅ 离线翻译结果: {result}")
            return result
    
    
    def _translate_with_deep_translator(self, text):
        """
        使用 deep_translator 进行翻译（推荐，更稳定）
        """
        for attempt in range(self.max_translation_retries):
            try:
                if attempt > 0:
                    print(f"🔄 重试翻译 ({attempt + 1}/{self.max_translation_retries})...")
                    time.sleep(1)
                else:
                    print("🌐 正在翻译成英文 (使用 DeepTranslator)...")
                
                # 尝试禁用代理（多种方法）
                saved_env = {}
                proxy_keys = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
                             'NO_PROXY', 'no_proxy', 'ALL_PROXY', 'all_proxy']
                
                try:
                    # 保存并清除代理环境变量
                    for key in proxy_keys:
                        if key in os.environ:
                            saved_env[key] = os.environ[key]
                            del os.environ[key]
                    
                    # 设置禁用代理
                    os.environ['NO_PROXY'] = '*'
                    
                    # 使用 requests session 明确禁用代理
                    if REQUESTS_AVAILABLE:
                        session = requests.Session()
                        session.trust_env = False  # 不使用系统代理
                        session.proxies = {"http": None, "https": None}
                        
                        # 使用自定义 session
                        import deep_translator.google as gt
                        old_session = getattr(gt, '_session', None)
                        gt._session = session
                    
                    # 执行翻译
                    translator = GoogleTranslator(source='auto', target='en')
                    english_text = translator.translate(text)
                    print(f"✅ 翻译结果: {english_text}")
                    return english_text
                    
                finally:
                    # 恢复环境变量
                    for key in proxy_keys:
                        if key in os.environ:
                            del os.environ[key]
                    for key, value in saved_env.items():
                        os.environ[key] = value
                    
                    # 恢复 session
                    if REQUESTS_AVAILABLE:
                        try:
                            if old_session is not None:
                                gt._session = old_session
                        except:
                            pass
                
            except Exception as e:
                error_msg = str(e)
                # 简化错误信息显示
                if 'ProxyError' in error_msg:
                    print(f"⚠️ 代理错误 (尝试 {attempt + 1}/{self.max_translation_retries}): 系统代理导致连接失败")
                elif 'SSLError' in error_msg or 'SSL' in error_msg:
                    print(f"⚠️ SSL错误 (尝试 {attempt + 1}/{self.max_translation_retries})")
                elif 'Max retries exceeded' in error_msg:
                    print(f"⚠️ 连接超时 (尝试 {attempt + 1}/{self.max_translation_retries})")
                else:
                    print(f"⚠️ 翻译错误 (尝试 {attempt + 1}/{self.max_translation_retries}): {type(e).__name__}")
                
                if attempt == self.max_translation_retries - 1:
                    print("❌ 在线翻译持续失败，自动切换到离线模式")
                    print("💡 原因: 系统代理设置导致无法访问 Google 翻译")
                    return None
        
        return None
    
    def _translate_with_googletrans(self, text):
        """
        使用 googletrans 进行翻译（备选方案）
        """
        import os
        
        for attempt in range(self.max_translation_retries):
            try:
                if attempt > 0:
                    print(f"🔄 重试翻译 ({attempt + 1}/{self.max_translation_retries})...")
                    time.sleep(1)
                else:
                    print("🌐 正在翻译成英文 (使用 GoogleTrans)...")
                
                # 临时禁用代理（避免代理导致的SSL错误）
                old_http_proxy = os.environ.get('HTTP_PROXY')
                old_https_proxy = os.environ.get('HTTPS_PROXY')
                old_http_proxy_lower = os.environ.get('http_proxy')
                old_https_proxy_lower = os.environ.get('https_proxy')
                
                try:
                    # 清除代理设置
                    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                        if key in os.environ:
                            del os.environ[key]
                    
                    # 重新创建翻译器实例
                    if attempt > 0:
                        self.translator = Translator(service_urls=['translate.google.com'])
                    
                    result = self.translator.translate(text, src='auto', dest='en')
                    english_text = result.text
                    print(f"✅ 翻译结果: {english_text}")
                    return english_text
                    
                finally:
                    # 恢复代理设置
                    if old_http_proxy:
                        os.environ['HTTP_PROXY'] = old_http_proxy
                    if old_https_proxy:
                        os.environ['HTTPS_PROXY'] = old_https_proxy
                    if old_http_proxy_lower:
                        os.environ['http_proxy'] = old_http_proxy_lower
                    if old_https_proxy_lower:
                        os.environ['https_proxy'] = old_https_proxy_lower
                
            except (ssl.SSLError, urllib3.exceptions.ProtocolError) as e:
                print(f"⚠️ SSL/代理错误 (尝试 {attempt + 1}/{self.max_translation_retries})")
                if attempt == self.max_translation_retries - 1:
                    print("❌ 在线翻译失败，自动切换到离线模式")
                    return None
                    
            except Exception as e:
                error_msg = str(e)
                # 检查是否是网络相关错误
                if any(keyword in error_msg for keyword in ['SSL', 'EOF occurred', '_ssl.c', 'ProxyError', 'Max retries']):
                    print(f"⚠️ 网络连接错误 (尝试 {attempt + 1}/{self.max_translation_retries})")
                    if attempt == self.max_translation_retries - 1:
                        print("❌ 在线翻译失败，自动切换到离线模式")
                        return None
                else:
                    print(f"❌ 翻译错误: {type(e).__name__}")
                    return None
        
        return None
    
    def recognize_speech_offline(self, audio):
        """
        离线语音识别(备用方法)
        
        注意: SpeechRecognition 3.10.0+ 已移除 recognize_sphinx 方法。
        如需真正的离线识别，请考虑：
        1. 降级到 SpeechRecognition 3.8.1 并安装 pocketsphinx
        2. 使用其他离线识别库如 vosk, whisper
        
        当前实现: 使用在线Google识别作为后备
        
        Args:
            audio: 音频数据
            
        Returns:
            str: 识别的文本，如果失败返回None
        """
        if audio is None:
            return None
            
        try:
            print("⚠️ 注意: 离线识别功能不可用，使用在线识别...")
            # recognize_sphinx 在新版本中已被移除
            # 使用 Google 识别作为后备方案
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"✅ 识别成功: {text}")
            return text
        except sr.UnknownValueError:
            print("❓ 无法识别语音内容")
            return None
        except sr.RequestError as e:
            print(f"❌ 识别服务错误: {e}")
            print("💡 提示: 如需离线识别，请使用 Vosk 或 Whisper 库")
            return None
        except AttributeError as e:
            print(f"❌ 方法不存在: {e}")
            print("💡 SpeechRecognition 新版本已移除 recognize_sphinx")
            return None
        except Exception as e:
            print(f"❌ 识别错误: {e}")
            return None
    
    def check_wake_word(self, text):
        """
        检查是否包含唤醒词
        
        Args:
            text: 识别的文本
            
        Returns:
            bool: 是否包含唤醒词
        """
        if text is None:
            return False
        return self.wake_word in text.lower()
    
    def wait_for_wake_word(self):
        """
        等待唤醒词
        持续监听直到听到唤醒词
        """
        while not self.is_awake:
            audio = self.listen_for_audio(timeout=10)
            if audio:
                text = self.recognize_speech(audio)
                if text:
                    if self.check_wake_word(text):
                        self.is_awake = True
                        return True
        return False
    
    def listen_and_recognize(self, timeout=5, phrase_time_limit=10):
        """
        监听并识别语音(一次性)
        
        Args:
            timeout: 等待开始说话的超时时间(秒)
            phrase_time_limit: 单次录音的最大时长(秒)
            
        Returns:
            str 或 dict: 如果启用翻译，返回{'original': 原文, 'translation': 译文}，否则返回识别文本
        """
        audio = self.listen_for_audio(timeout, phrase_time_limit)
        if audio:
            text = self.recognize_speech(audio)
            if text:
                print(f"✅ 识别结果: {text}")
                
                # 如果启用了翻译，则翻译成英文
                if self.enable_translation:
                    translation = self.translate_to_english(text)
                    return {
                        'original': text,
                        'translation': translation
                    }
                return text
        return None
    
    def continuous_listen(self, callback=None, wake_word_required=True):
        """
        持续监听模式
        
        Args:
            callback: 回调函数，接收识别结果作为参数（如果启用翻译，接收dict；否则接收str）
            wake_word_required: 是否需要唤醒词
        """
        print("🎧 进入持续监听模式...")
        
        if wake_word_required:
            self.wait_for_wake_word()
        
        self.is_listening = True
        
        try:
            while self.is_listening:
                audio = self.listen_for_audio(timeout=5)
                if audio:
                    text = self.recognize_speech(audio)
                    if text:
                        print(f"✅ 识别结果: {text}")
                        
                        # 检查退出命令
                        if "退出" in text or "再见" in text:
                            print("👋 收到退出命令")
                            self.is_listening = False
                            self.is_awake = False
                            break
                        
                        # 如果启用了翻译，进行翻译并返回字典
                        if self.enable_translation:
                            translation = self.translate_to_english(text)
                            result = {
                                'original': text,
                                'translation': translation
                            }
                        else:
                            result = text
                        
                        # 调用回调函数
                        if callback:
                            callback(result)
                            
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断")
            self.is_listening = False
            self.is_awake = False
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        self.is_awake = False
        print("⏹️ 已停止监听")


def demo_basic():
    """基础演示: 单次语音识别"""
    print("=" * 50)
    print("基础演示: 单次语音识别")
    print("=" * 50)
    
    # 询问是否启用翻译
    print("\n是否启用翻译功能？")
    print("1. 是（在线翻译）")
    print("2. 否")
    
    choice = input("请选择 (1/2, 默认2): ").strip() or "2"
    
    enable_translation = (choice == "1")
    offline_mode = False
    
    if enable_translation:
        print("\n已启用翻译模式\n")
    
    assistant = VoiceAssistant(enable_translation=enable_translation, offline_mode=offline_mode)
    result = assistant.listen_and_recognize(timeout=5, phrase_time_limit=10)
    if result:
        if isinstance(result, dict):
            if result['translation']:
                print(result['translation'])
            else:
                print(result['original'])
        else:
            print(result)
    else:
        print("未识别到语音")


def demo_continuous():
    """唤醒词循环演示 - 每次唤醒后只识别一次"""
    print("=" * 50)
    print("唤醒词循环演示")
    print("=" * 50)
    
    # 询问是否启用翻译
    print("\n是否启用翻译功能？")
    print("1. 是（在线翻译）")
    print("2. 否")
    
    choice = input("请选择 (1/2, 默认2): ").strip() or "2"
    
    enable_translation = (choice == "1")
    offline_mode = False
    
    if enable_translation:
        print("\n已启用翻译模式")
    
    print("每次唤醒后只识别一次")
    print("Ctrl+C 退出\n")
    
    assistant = VoiceAssistant(wake_word="小助手", enable_translation=enable_translation, offline_mode=offline_mode)
    
    try:
        while True:
            # 等待唤醒词
            print("等待唤醒词: '小助手'...")
            if assistant.wait_for_wake_word():
                print("已唤醒\n")
                
                # 识别一次命令
                result = assistant.listen_and_recognize(timeout=5, phrase_time_limit=10)
                
                if result:
                    # 处理识别结果
                    if isinstance(result, dict):
                        text = result['original']
                        translation = result.get('translation')
                        if translation:
                            print(translation)
                        else:
                            print(text)
                    else:
                        text = result
                        print(text)
                    
                    # 检查退出命令
                    if "退出" in text or "再见" in text:
                        print("\n程序结束")
                        break
                    
                    # 重置为未唤醒状态
                    assistant.is_awake = False
                    print()
                else:
                    print("未识别到命令\n")
                    assistant.is_awake = False
                    
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════╗
    ║     Python 语音助手演示程序          ║
    ╚═══════════════════════════════════════╝
    
    请选择演示模式:
    1. 基础演示 - 单次语音识别
    2. 唤醒词循环 - 每次唤醒后识别一次命令
    """)
    
    try:
        choice = input("请输入选择 (1/2): ").strip()
        
        if choice == "1":
            demo_basic()
        elif choice == "2":
            demo_continuous()
        else:
            print("无效选择，运行基础演示...")
            demo_basic()
            
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 错误: {e}")
