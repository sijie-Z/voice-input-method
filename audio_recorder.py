import queue
import threading
import wave
import numpy as np


class AudioRecorder:
    """音频录制模块，基于 sounddevice InputStream 非阻塞模式。"""

    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self._queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self._audio_data = []

    def _callback(self, indata, frames, time, status):
        """sounddevice InputStream 回调，将音频块放入队列。"""
        if status:
            print(f"[AudioRecorder] 状态警告: {status}")
        self._queue.put(indata.copy())

    def _record_thread(self):
        """录音线程目标函数，创建 InputStream 并等待停止事件。"""
        import sounddevice as sd

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16",
                callback=self._callback,
            ):
                self._stop_event.wait()
        except Exception as e:
            print(f"[AudioRecorder] 录音线程异常: {e}")

    def start_recording(self):
        """开始录音，创建并启动录音线程。"""
        import sounddevice as sd

        try:
            sd.query_devices()  # 快速验证是否有音频设备
        except Exception as e:
            print(f"[AudioRecorder] 无可用音频设备: {e}")
            raise

        self._stop_event.clear()
        self._audio_data = []
        self._thread = threading.Thread(target=self._record_thread, daemon=True)
        self._thread.start()
        print("[AudioRecorder] 录音已开始...")

    def stop_recording(self):
        """停止录音，从队列取出所有数据，保存为 WAV 文件。"""
        if not self._thread or not self._thread.is_alive():
            print("[AudioRecorder] 没有正在进行的录音。")
            return

        self._stop_event.set()
        self._thread.join(timeout=5)

        # 从队列中取出所有音频数据
        samples = []
        while not self._queue.empty():
            samples.append(self._queue.get_nowait())

        if not samples:
            print("[AudioRecorder] 未捕获到音频数据。")
            return

        audio_array = np.concatenate(samples, axis=0)

        # 保存为 WAV 文件
        import os

        os.makedirs("temp", exist_ok=True)
        filepath = "temp/recorded.wav"

        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit = 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_array.tobytes())

        print(f"[AudioRecorder] 录音完成，已保存到 {filepath}")


if __name__ == "__main__":
    import time

    try:
        recorder = AudioRecorder(sample_rate=16000)
        recorder.start_recording()
        print("录音中... 3 秒后自动停止。")
        time.sleep(3)
        recorder.stop_recording()
        print("录音完成，已保存到 temp/recorded.wav")
    except Exception as e:
        print(f"录音出错: {e}")
