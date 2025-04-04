# -*- coding: utf-8 -*-
import os
import logging
from pocketsphinx import LiveSpeech, get_model_path

# 初始化日志模块
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')
def wake_up():
    mode_path = r"./pocketsphinx_model/acoustic-model"
    bin_path = r"./pocketsphinx_model/language-model.lm.bin"
    dict_path = r"./pocketsphinx_model/pronounciation-dictionary.dict"
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=mode_path,
        lm=bin_path,
        dic=dict_path
    )
    for phrase in speech:
        logging.info(f"wake_up phrase: {phrase}")
        logging.info(f"phrase.segments: {phrase.segments(detailed=True)}")
        # 只要命中上述关键词的内容，都算对
        if str(phrase) in ["小包", "小雹", "小宝", "小鲍"]:
            logging.info("正确识别唤醒词")
            return True


if __name__ == "__main__":
    wake_up()
