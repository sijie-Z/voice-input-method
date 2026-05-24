import os


class TextPolisher:
    """AI 文本润色，将口语化语音识别文本转为书面语。"""

    SYSTEM_PROMPTS = {
        "general": (
            "你是一个文本润色助手。请将用户输入的口语化语音识别文本转为规范的书面语："
            "去口语化、补充标点符号、修正错别字、整理语序。"
            "保持原意不变，只输出润色后的文本，不要添加任何解释。"
        ),
        "meeting": (
            "你是一个会议纪要助手。请将语音识别后的会议语音转为规范的会议纪要："
            "提炼关键结论、行动项和决策点。使用结构化格式输出。"
            "只输出润色后的文本，不要添加任何解释。"
        ),
        "email": (
            "你是一个邮件撰写助手。请将语音输入的邮件草稿转为正式邮件格式："
            "包含得体的称呼、正文和落款。语气专业但不生硬。"
            "只输出润色后的文本，不要添加任何解释。"
        ),
        "social": (
            "你是一个社交媒体文本助手。请修正语音输入文本中的错别字和标点，"
            "保留轻松自然的语气和口语化风格，让表达更流畅。"
            "只输出润色后的文本，不要添加任何解释。"
        ),
    }

    def __init__(self, api_key=None):
        self._client = None
        api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                print("TextPolisher 初始化成功")
            except Exception as e:
                print(f"TextPolisher 初始化失败: {e}")
        else:
            print("未设置 API key，润色功能不可用。请设置环境变量 OPENAI_API_KEY 或 DEEPSEEK_API_KEY")

    def polish(self, text, mode="general"):
        """润色文本，失败时返回原始文本。"""
        if self._client is None:
            return text

        if not text.strip():
            return text

        system_prompt = self.SYSTEM_PROMPTS.get(mode, self.SYSTEM_PROMPTS["general"])

        try:
            response = self._client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
            )
            result = response.choices[0].message.content.strip()
            return result if result else text
        except Exception as e:
            print(f"润色请求失败: {e}，使用原始文本")
            return text
