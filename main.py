from voice_typer import VoiceTyper


if __name__ == "__main__":
    typer = VoiceTyper(hot_words=["七牛云", "XEngineer", "语音输入法"])
    typer.start()
