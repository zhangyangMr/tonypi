import time
import threading
import os
import hiwonder.TTS as TTS
import hiwonder.ActionGroupControl as AGC

tts = TTS.TTS()
AGC.runActionGroup('stand')                                                        # 参数为动作组的名称，不包含后缀，以字符形式传入(the parameter is the name of the action group, without the file extension, passed as a string)

# AGC.runActionGroup('bow_down', times=1, with_stand=True)
threading.Thread(target=AGC.runActionGroup, args=('bow_down', 3, True)).start()
os.system('aplay /home/pi/TonyPi/Example/test1.wav')
os.system('aplay /home/pi/TonyPi/Example/test.wav')
# tts.TTSModuleSpeak('[h0][v1]', '新春快乐 吉祥如意')
# time.sleep(20)
AGC.runActionGroup('bow_up', times=1, with_stand=True)
AGC.stopActionGroup()                                                              # 前进3秒后停止(move forward for 3 seconds and then stop)
