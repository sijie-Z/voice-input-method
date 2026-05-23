# 语音指令引擎 — 设计文档

## 1. 概述

语音指令引擎是语音输入法的「王牌功能」：用户说出的语音经过 Vosk 识别后，先匹配预设指令集，命中则执行系统操作（如换行、删除、搜索），未命中则走常规的文本润色流程并上屏。

### 核心价值
- 从「只会打字」升级为「能听懂并执行命令」
- 彻底解放双手，覆盖编辑效率场景
- 与 AI 润色形成互补：指令负责操作，润色负责文本质量

## 2. 指令匹配规则

采用两级匹配策略，按优先级从高到低：

### 2.1 精确匹配
识别文本与指令触发词**完全一致**时命中。
```
"换行"          → 命中【换行】
"撤销"          → 命中【撤销】
```

### 2.2 前缀匹配
识别文本**以触发词开头**时命中，提取剩余部分作为参数。
```
"搜索 七牛云"   → 命中【搜索】，参数="七牛云"
"打开 计算器"   → 命中【打开】，参数="计算器"
```

匹配优先级：精确匹配 > 前缀匹配。同一文本命中多条时，选择触发词**长度最长**的指令。

## 3. 指令表

| 触发词 | 对应操作 | 实现方式 |
|--------|----------|----------|
| 换行 | 模拟回车键 | `pynput.keyboard.Controller.press(Key.enter)` |
| 删除一句 | Ctrl+Shift+Left 选中前一句 + Backspace 删除 | `Controller` 组合键模拟 |
| 全部删除 | Ctrl+A 全选 + Backspace 删除 | 两步组合键 |
| 全部复制 | Ctrl+A 全选 + Ctrl+C 复制到剪贴板 | 两步组合键 |
| 粘贴 | Ctrl+V 粘贴 | 单次组合键 |
| 撤销 | Ctrl+Z 撤销 | 单次组合键 |
| 搜索 | 剪贴板复制关键词 → 打开浏览器搜索 | `webbrowser.open(url)` |
| 打开 | 启动指定 Windows 程序 | `subprocess.Popen(程序路径)` |
| 截屏 | Win+Shift+S 截图工具 | 三键组合键 |
| 锁屏 | Win+L 锁定 | 双键组合键 |
| 大写切换 | 模拟 CapsLock 按键 | `Controller.press(Key.caps_lock)` |

> **注**："搜索"和"打开"是前缀匹配指令，需要提取参数。

## 4. 处理流程

```
                  ┌─────────────────────────┐
                  │   Vosk 识别输出文本     │
                  └─────────┬───────────────┘
                            │
                            ▼
                  ┌─────────────────────────┐
                  │    CommandEngine        │
                  │    检查是否命中指令      │
                  └─────────┬───────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
     ┌─────────────────┐       ┌──────────────────────┐
     │   命中指令       │       │    未命中指令         │
     │ 执行对应操作      │       │   → AI 润色          │
     │ (按键/程序/网页)  │       │   → 上屏到当前窗口    │
     └─────────────────┘       └──────────────────────┘
```

## 5. 技术实现方案

### 5.1 CommandEngine 类

在 `main.py` 中新增 `CommandEngine` 类，职责：

```python
class CommandEngine:
    """语音指令引擎：匹配指令并执行系统操作。"""

    def __init__(self):
        self._kb = Controller()
        self._commands = []  # list of (trigger, type, handler)
        self._register_commands()

    def _register_commands(self):
        """注册所有指令到映射表。"""

    def match(self, text):
        """返回 (matched_cmd, argument) 或 (None, None)。"""

    def execute(self, cmd, arg):
        """执行指令对应的操作。"""
```

### 5.2 指令注册方式

指令用元组表维护，每行定义：
```python
[
    ("换行",     "exact",   lambda kb, arg: kb.press(Key.enter)),
    ("搜索",     "prefix",  lambda kb, arg: webbrowser.open(f"https://www.baidu.com/s?wd={arg}")),
]
```

- `"exact"` — 精确匹配
- `"prefix"` — 前缀匹配，提取参数

### 5.3 集成到 VoiceTyper

在 `VoiceTyper.stop_recording()` 中，Vosk 输出文本后先送入 `CommandEngine.match()`：

```python
def stop_recording(self):
    self.recorder.stop_recording()
    text = self._recognize("temp/recorded.wav")
    if not text:
        return

    cmd, arg = self._cmd_engine.match(text)
    if cmd:
        self._cmd_engine.execute(cmd, arg)
        return

    # 未命中指令：润色 + 上屏
    polished = self._polisher.polish(text)
    self._type_text(polished)
```

## 6. 注意事项

### 6.1 按键组合时序
组合键（如 Ctrl+A）需要严格顺序：先按下 modifier，再按字母键，释放时逆序。
```
kb.press(Key.ctrl)       # 先按 Ctrl
kb.press('a')            # 再按 A
kb.release('a')          # 先松 A
kb.release(Key.ctrl)     # 再松 Ctrl
```

### 6.2 中英文输入法冲突
模拟按键时如果当前输入法为中文模式，Ctrl+字母可能被拦截为标点输入。建议在关键组合键前短暂切换为英文模式，或使用 `SendKeys` 替代方案。

### 6.3 参数提取安全性
"搜索"指令接受用户参数并拼接 URL，需要对参数做 URL 编码，防止特殊字符破坏 URL 结构。

### 6.4 指令误触防护
短触发词（如"打开"）容易在日常语音中误触。解决方案：
- 仅在**静默停顿后**的首句做匹配
- 或要求指令前后有明确停顿（Vosk 可通过 `final` 标记判断）

## 7. 扩展方向（未来迭代）

- 支持连续叠加指令："换行后粘贴"
- 用户自定义指令：通过配置文件 `commands.json` 扩展
- 应用上下文感知：在记事本中禁用浏览器相关指令
