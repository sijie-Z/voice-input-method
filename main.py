from audio_recorder import AudioRecorder
from pynput import keyboard


class VoiceTyper:
    """语音输入控制器，将录音与键盘热键结合。"""

    def __init__(self):
        self.recorder = AudioRecorder(sample_rate=16000)
        self._is_recording = False
        self._listener = None

    def _on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_r and not self._is_recording:
                self._is_recording = True
                self.recorder.start_recording()
                print("开始录音...")
            elif key == keyboard.Key.esc:
                print("退出程序...")
                return False  # 停止监听
        except Exception as e:
            print(f"按键处理异常: {e}")

    def _on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_r and self._is_recording:
                self._is_recording = False
                self.recorder.stop_recording()
                print("录音结束，文件已保存到 temp/recorded.wav")
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
    typer = VoiceTyper()
    typer.start()
