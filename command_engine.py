import subprocess
import urllib.parse
import webbrowser

import pyautogui


class CommandEngine:
    """语音指令引擎：匹配指令关键词并执行对应系统操作。"""

    def __init__(self, mode_setter=None):
        # (trigger, type, description, handler)
        # type: "exact" 精确匹配 / "prefix" 前缀匹配
        self._commands = []

        # --- 润色模式切换指令 ---
        if mode_setter:
            self._add_exact("润色模式", "切换为通用润色",
                            lambda: mode_setter("general"))
            self._add_exact("会议模式", "切换为会议纪要润色",
                            lambda: mode_setter("meeting"))
            self._add_exact("邮件模式", "切换为邮件格式润色",
                            lambda: mode_setter("email"))
            self._add_exact("朋友圈模式", "切换为社交轻松润色",
                            lambda: mode_setter("social"))

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
