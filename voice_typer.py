import json
import time
import wave

import pyautogui
import pyperclip
from audio_recorder import AudioRecorder
from command_engine import CommandEngine
from pynput import keyboard
from text_polisher import TextPolisher


class VoiceTyper:
    """语音输入控制器，将录音与键盘热键结合，集成 Vosk 离线识别、语音指令和 AI 润色。"""

    def __init__(self, hot_words=None, polish_mode="general"):
        self.recorder = AudioRecorder(sample_rate=16000)
        self._is_recording = False
        self._listener = None
        self._hot_words = hot_words or []
        self._model = None
        self._cmd_engine = CommandEngine(mode_setter=self.set_polish_mode)
        self._polisher = TextPolisher()
        self._polish_mode = polish_mode
        self.load_model()
        print(f"当前润色模式：{self._mode_label(self._polish_mode)}")

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

    def _mode_label(self, mode):
        labels = {"general": "通用", "meeting": "会议纪要", "email": "邮件", "social": "朋友圈"}
        return labels.get(mode, mode)

    def set_polish_mode(self, mode):
        """切换润色模式，控制台反馈。"""
        self._polish_mode = mode
        msg = f"已切换到{self._mode_label(mode)}模式"
        print(msg)

    def _type_text(self, text):
        """将文本通过剪贴板粘贴到当前活动窗口。"""
        if not text.strip():
            return
        try:
            pyperclip.copy(text)
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "v")
            print(f"已上屏：{text}")
        except Exception as e:
            print(f"上屏失败: {e}")

    def stop_recording(self):
        """停止录音，保存 WAV，执行 Vosk 识别，先匹配指令再润色上屏。"""
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

        # 未命中指令，润色后上屏
        polished = self._polisher.polish(text, mode=self._polish_mode)
        self._type_text(polished)

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
