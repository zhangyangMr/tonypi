import pyttsx3


def play_sound(text):
    """
     使用pyttsx3进行语音合成。

     :param text: 需要合成语音的文字
     """
    engine = pyttsx3.init()
    # rate = engine.getProperty('rate')
    # engine.setProperty('rate', rate + 20)  # 调整语速
    # engine.setProperty('voice', 'Chinese (Mandarin, latin as Pinyin)')
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def get_voice_list():
    """获取pyttsx3支持的语音列表。"""
    voices = pyttsx3.init().getProperty('voices')
    for voice in voices:
        # print(voice.id, voice.name, voice.languages, voice.gender, voice.age)
        print(voice.id)


if __name__ == '__main__':
    play_sound('你好，我是小爱同学')
    # get_voice_list()
