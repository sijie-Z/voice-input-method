from voice_typer import VoiceTyper


if __name__ == "__main__":
    typer = VoiceTyper(hot_words=[
        "七牛云", "XEngineer", "语音输入法",
        "换行", "删除", "撤销", "保存", "复制", "粘贴",
        "截屏", "锁屏", "搜索", "打开", "记事本", "大写",
        "润色模式", "会议模式", "邮件模式", "朋友圈模式",
        "人工智能",
    ])
    typer.start()
