import json
import wave
import webbrowser
import subprocess
import urllib.parse

import pyautogui
from audio_recorder import AudioRecorder
from pynput import keyboard


class CommandEngine:
    """语音指令引擎：匹配指令关键词并执行对应系统操作。"""

    def __init__(self):
        # (trigger, type, description, handler)
        # type: "exact" 精确匹配 / "prefix" 前缀匹配
        self._commands = []

        # --- 精确匹配指令 ---
        self._add_exact("换行", "模拟回车键",
                        lambda: pyautogui.press("enter"))

        self._add_exact("删除上一句", "Ctrl+Shift+Left + Backspace",
                        lambda: self._del_prev_sentence())

        self._add_exact("全部删除", "Ctrl+A + Backspace",
                        lambda: self._select_all_and_backspace())

        self._add_exact("全部复制", "Ctrl+A + Ctrl+C",
                        lambda: self._select_all_and_copy())

        self._add_exact("粘贴", "Ctrl+V",
                        lambda: pyautogui.hotkey("ctrl", "v"))

        self._add_exact("撤销", "Ctrl+Z",
                        lambda: pyautogui.hotkey("ctrl", "z"))

        self._add_exact("保存", "Ctrl+S",
                        lambda: pyautogui.hotkey("ctrl", "s"))

        self._add_exact("锁屏", "Win+L",
                        lambda: pyautogui.hotkey("win", "l"))

        self._add_exact("截屏", "Win+Shift+S",
                        lambda: pyautogui.hotkey("win", "shift", "s"))

        self._add_exact("大写切换", "CapsLock",
                        lambda: pyautogui.press("capslock"))

        self._add_exact("打开记事本", "启动 notepad.exe",
                        lambda: subprocess.Popen("notepad.exe"))

        # --- 前缀匹配指令 ---
        self._add_prefix("搜索", "打开浏览器搜索",
                         lambda kw: webbrowser.open(
                             f"https://www.google.com/search?q={urllib.parse.quote(kw)}"
                         ))

        # 按触发词长度降序排序，长词优先匹配
        self._commands.sort(key=lambda c: len(c[0]), reverse=True)

    def _add_exact(self, trigger, description, handler):
        self._commands.append((trigger, "exact", description, handler))

    def _add_prefix(self, trigger, description, handler):
        self._commands.append((trigger, "prefix", description, handler))

    def _del_prev_sentence(self):
        pyautogui.hotkey("ctrl", "shift", "left")
        pyautogui.press("backspace")

    def _select_all_and_backspace(self):
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")

    def _select_all_and_copy(self):
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")

    def match(self, text):
        """精确/前缀匹配指令，返回 (trigger, handler, arg) 或 None。"""
        if not text:
            return None

        # 精确匹配
        for trigger, ctype, _desc, handler in self._commands:
            if ctype == "exact" and text == trigger:
                return (trigger, handler, None)

        # 前缀匹配
        for trigger, ctype, _desc, handler in self._commands:
            if ctype == "prefix" and text.startswith(trigger):
                arg = text[len(trigger):].strip()
                return (trigger, handler, arg)

        return None

    def execute(self, handler, arg):
        """执行指令对应的操作。"""
        if arg is not None:
            handler(arg)
        else:
            handler()


class VoiceTyper:
    """语音输入控制器，将录音与键盘热键结合，集成 Vosk 离线识别和语音指令。"""

    def __init__(self, hot_words=None):
        self.recorder = AudioRecorder(sample_rate=16000)
        self._is_recording = False
        self._listener = None
        self._hot_words = hot_words or []
        self._model = None
        self._cmd_engine = CommandEngine()
        self.load_model()

    def load_model(self):
        """加载 Vosk 离线模型，失败时打印错误不崩溃。"""
        try:
            from vosk import Model
            self._model = Model("models/vosk-model-small-cn-0.22")
            print(f"Vosk 模型加载成功，热词列表: {self._hot_words}")
        except Exception as e:
            print(f"Vosk 模型加载失败: {e}，将使用纯录音模式")

    def _recognize(self, wav_path):
        """对 WAV 文件执行 Vosk 识别，返回文本。"""
        if self._model is None:
            return ""

        from vosk import KaldiRecognizer

        try:
            wf = wave.open(wav_path, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                print(f"不支持的音频格式: channels={wf.getnchannels()}, width={wf.getsampwidth()}")
                wf.close()
                return ""

            rec = KaldiRecognizer(self._model, wf.getframerate())

            if self._hot_words:
                rec.SetWords(True)
                for word in self._hot_words:
                    rec.AddWord(word)

            data = wf.readframes(wf.getnframes())
            rec.AcceptWaveform(data)
            result = json.loads(rec.FinalResult())
            text = result.get("text", "")
            wf.close()
            return text
        except FileNotFoundError:
            print(f"识别失败: 找不到文件 {wav_path}")
            return ""
        except Exception as e:
            print(f"识别异常: {e}")
            return ""

    def stop_recording(self):
        """停止录音，保存 WAV，执行 Vosk 识别，先匹配指令再决定上屏。"""
        self.recorder.stop_recording()
        text = self._recognize("temp/recorded.wav")

        if not text:
            print("识别结果：（无有效语音）")
            return

        # 先匹配指令
        matched = self._cmd_engine.match(text)
        if matched:
            trigger, handler, arg = matched
            try:
                self._cmd_engine.execute(handler, arg)
                print(f"执行指令：{trigger}")
            except Exception as e:
                print(f"指令执行失败 [{trigger}]: {e}")
            return

        # 未命中指令，走上屏流程（明天接润色）
        print(f"上屏文本：{text}")

    def _on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_r and not self._is_recording:
                self._is_recording = True
                self.recorder.start_recording()
                print("开始录音...")
            elif key == keyboard.Key.esc:
                print("退出程序...")
                return False
        except Exception as e:
            print(f"按键处理异常: {e}")

    def _on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_r and self._is_recording:
                self._is_recording = False
                self.stop_recording()
        except Exception as e:
            print(f"按键处理异常: {e}")

    def start(self):
        """启动键盘监听。"""
        print("语音输入法已启动，按住右 Ctrl 开始录音，松开停止，按 Esc 退出")
        with keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        ) as self._listener:
            self._listener.join()

    def stop(self):
        """停止键盘监听。"""
        if self._listener is not None:
            self._listener.stop()


if __name__ == "__main__":
    typer = VoiceTyper(hot_words=["七牛云", "XEngineer", "语音输入法"])
    typer.start()
