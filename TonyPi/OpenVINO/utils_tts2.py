import hiwonder.TTS as TTS

def tts(TEXT=''):
    tts = TTS.TTS()
    tts.TTSModuleSpeak('[v10]', TEXT)
    

print('TTS 开始')

with open('/home/pi/TonyPi/OpenVINO/temp/ai_response.txt', 'r', encoding='utf-8') as f:
    agent_plan = f.read()
try:
    tts(agent_plan)
except:
    print('语音为空，退出')
    exit()
