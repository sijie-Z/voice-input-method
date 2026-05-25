# 语音输入法 — 离线智能语音输入工具

基于 Vosk 离线语音识别 + DeepSeek AI 润色的 Windows 语音输入法。按住右 Ctrl 说话，松开后自动识别、润色并上屏到当前窗口，全程离线优先、联网增强。

## 功能演示

> [离线语音输入法演示视频](https://www.bilibili.com/video/BV14JGR6wExC/)

## 核心功能

| 功能 | 说明 |
|------|------|
| **离线语音识别** | 基于 Vosk 中文小模型，无需联网即可将语音转为文字 |
| **AI 文本润色** | 接入 DeepSeek API，自动去口语化、补标点、整理语序（可选） |
| **语音指令引擎** | 16 条语音命令，包括系统操作（换行/删除/复制/保存/截屏/锁屏）和浏览器搜索 |
| **四种润色模式** | 通用润色、会议纪要、邮件撰写、朋友圈风格，语音随时切换 |
| **热词支持** | 可配置热词列表，提升专有名词识别准确率 |

## 安装与运行

### 环境要求

- Python 3.9+
- Windows 10/11
- 麦克风设备

### 安装步骤

```bash
# 1. 克隆仓库
git clone git@github.com:sijie-Z/voice-input-method.git
cd voice-input-method

# 2. 安装依赖
pip install -r requirements.txt
├── tests/                  # 单元测试（26 个用例）

# 3. 下载 Vosk 中文模型（约 42MB）
python -c "
import urllib.request, zipfile, os
url = 'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip'
urllib.request.urlretrieve(url, 'model.zip')
with zipfile.ZipFile('model.zip', 'r') as zf:
    zf.extractall('models/')
os.remove('model.zip')
print('模型下载完成')
"

# 4. （可选）设置 DeepSeek API Key 以启用 AI 润色
# Windows:
set OPENAI_API_KEY=sk-your-key-here
# Linux/macOS:
export OPENAI_API_KEY=sk-your-key-here
# 或设置 DEEPSEEK_API_KEY，效果相同
```

> **不设置 API key 也能正常使用**，识别后的文本会直接上屏，仅跳过 AI 润色步骤。

### 运行

```bash
python main.py
```

启动后控制台显示提示信息，表示输入法已就绪。

## 使用说明

### 基本操作

| 操作 | 方式 |
|------|------|
| 开始录音 | 按住 **右 Ctrl** |
| 停止录音并上屏 | 松开 **右 Ctrl** |
| 退出程序 | 按 **Esc** |

### 语音指令清单

对着麦克风说出以下指令即可执行对应操作：

| 指令 | 操作 | 匹配方式 |
|------|------|----------|
| 换行 | 模拟回车键 | 精确 |
| 删除上一句 | 选中前一句并删除 | 精确 |
| 全部删除 | 全选并删除 | 精确 |
| 全部复制 | 全选并复制 | 精确 |
| 粘贴 | Ctrl+V | 精确 |
| 撤销 | Ctrl+Z | 精确 |
| 保存 | Ctrl+S | 精确 |
| 锁屏 | Win+L | 精确 |
| 截屏 | Win+Shift+S | 精确 |
| 大写切换 | CapsLock | 精确 |
| 打开记事本 | 启动 notepad.exe | 精确 |
| 搜索 XXX | 浏览器搜索关键词 | 前缀 |
| 润色模式 | 切换为通用润色 | 精确 |
| 会议模式 | 切换为会议纪要润色 | 精确 |
| 邮件模式 | 切换为邮件格式润色 | 精确 |
| 朋友圈模式 | 切换为社交轻松润色 | 精确 |

> 指令匹配规则：先精确匹配，再前缀匹配，长触发词优先。识别到指令后仅执行操作，不会上屏。

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.12 | 主语言 |
| `vosk` | 离线中文语音识别引擎 |
| `pynput` | 全局键盘监听（热键捕获） |
| `sounddevice` | 麦克风音频采集 |
| `pyautogui` | 模拟键盘输入和组合键 |
| `pyperclip` | 剪贴板操作（文本上屏桥梁） |
| `openai` | 调用 DeepSeek API 进行文本润色 |
| `wave` / `numpy` | WAV 音频文件读写 |

## 项目架构

```
voice-input-method/
├── main.py                 # 入口文件（仅导入和启动）
├── voice_typer.py          # 核心控制器：串联录音、识别、指令、润色、上屏
├── audio_recorder.py       # 音频录制模块：麦克风采集 + WAV 保存
├── command_engine.py       # 语音指令引擎：16条命令的注册、匹配、执行
├── text_polisher.py        # AI 润色模块：四种模式 + DeepSeek API 调用
├── requirements.txt        # Python 依赖清单
├── tests/                  # 单元测试（26 个用例）
├── models/                 # Vosk 离线模型文件
├── temp/                   # 临时音频文件
└── README.md               # 项目文档
```

### 数据流

```
麦克风 → AudioRecorder → WAV 文件 → Vosk 识别 → 文本
                                                      ↓
                                           CommandEngine 匹配
                                          ↙                    ↘
                                    命中指令                  未命中
                                    执行操作              TextPolisher 润色
                                                            ↓
                                                      pyperclip + Ctrl+V 上屏
```

## 评审信息

- **选题**：语音输入法（七牛云 × XEngineer 暑期实训营 第一批次）
- **开发周期**：2026.05.23 – 2026.05.25
- **提交内容**：公开仓库 + Demo 视频 + README

## 致谢

- [Vosk](https://alphacephei.com/vosk/) — 离线语音识别引擎
- [DeepSeek](https://platform.deepseek.com/) — AI 文本润色
- 本项目部分代码由 AI 辅助生成

## License

MIT
