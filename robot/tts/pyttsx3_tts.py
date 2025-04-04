import pyttsx3

# 初始化语音合成引擎

def play_sound(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + 20)  # 调整语速
    engine.say(text)
    engine.runAndWait()
    engine.stop()
