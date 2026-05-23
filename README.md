# 语音输入法

基于 Vosk 离线语音识别 + DeepSeek AI 润色的语音输入法。

## 功能

- **语音录制**：按住右 Ctrl 录音，松开停止
- **离线识别**：Vosk 中文小模型，无需联网
- **语音指令**：12 种语音命令（换行、删除、复制、搜索等）
- **AI 润色**：四种模式（通用、会议纪要、邮件、朋友圈）

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## AI 润色配置（可选）

设置环境变量以启用 AI 文本润色（不设置也能正常使用基础输入功能）：

```bash
set OPENAI_API_KEY=sk-your-key-here     # Windows
export OPENAI_API_KEY=sk-your-key-here  # Linux/macOS
```

或设置 `DEEPSEEK_API_KEY`，效果相同。

API 来源：DeepSeek（https://platform.deepseek.com），兼容 OpenAI SDK 格式。

## 使用方式

| 操作 | 按键 |
|------|------|
| 开始录音 | 按住右 Ctrl |
| 停止录音 | 松开右 Ctrl |
| 退出程序 | 按 Esc |

## 语音指令

| 指令 | 操作 |
|------|------|
| 换行 | 回车 |
| 删除上一句 | 删除前一句 |
| 全部删除 | 全选删除 |
| 粘贴 | Ctrl+V |
| 搜索 XXX | 浏览器搜索 |
| 更多... | 见 CommandEngine |

## 项目结构

```
voice-input-method/
├── main.py              # 主程序入口
├── audio_recorder.py    # 音频录制模块
├── requirements.txt     # Python 依赖
├── models/              # Vosk 模型
├── temp/                # 临时音频文件
└── README.md
```

## License

MIT
