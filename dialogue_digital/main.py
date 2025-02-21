# -*- coding: utf-8 -*-

import pyaudio
import logging
import json

from sound_to_text import AsrOnline
from text_to_sound import TTSClient

from cfg_utils import read_llm_cfg, reflect_json_2_class
from llm_config import LLMConfig, MaasApiConf
from llm import init_maasapi_llm_chain
from utils import starts_with_chinese_pinyin
from utils_robot import *

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

if __name__ == '__main__':
    cfg_path = "./llm_conf.yaml"

    # 初始化MaaS大模型
    llm_cfg = read_llm_cfg(cfg_path)
    model_detail_config = reflect_json_2_class(llm_cfg, LLMConfig)
    logging.info(f"model_detail_config: {model_detail_config}")

    maas_api_cfg = reflect_json_2_class(model_detail_config.maas_api_conf, MaasApiConf)

    maas_chain = init_maasapi_llm_chain(model_detail_config, "common_use")

    # 音频参数
    FORMAT = pyaudio.paInt16  # 16位深度
    CHANNELS = 1  # 单声道
    RATE = 16000  # 采样率
    CHUNK = 960  # 每个缓冲区的帧数

    # 初始化pyaudio
    p = pyaudio.PyAudio()

    # 打开音频流
    input_stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
    # 初始化asr
    asr_client = AsrOnline(
        uri=maas_api_cfg.asr_url, is_ssl=False,
        chunk_size="-1, 10, 5", mode="2pass")

    # 初始化TTS
    tts_uri = maas_api_cfg.tts_url
    tts_client = TTSClient(tts_uri)
    tts_client.start()

    try:
        while True:
            # 从麦克风持续读取数据
            # logging.info("开始从麦克风读取音频数据...")
            data = input_stream.read(CHUNK, exception_on_overflow=False)

            asr_msg = asr_client.feed_chunk(data, wait_time=0.02)
            # logging.info(f"asr_msg: {asr_msg}")

            if len(asr_msg) > 0:
                if starts_with_chinese_pinyin(asr_msg["text"], "小明同学"):
                    chat_response = maas_chain.chat(asr_msg["text"], False)
                    if chat_response.status_code == 200:
                        chat_result = chat_response.json()
                        if chat_result.get("code") == 200:
                            chat_text = chat_result["data"]["text"]

                            chat_text = chat_text.replace("'", '"')
                            chat_text_json = json.loads(chat_text)

                            action = chat_text_json["action"]
                            res_text = chat_text_json["response"]
                            logging.info(f"chat_text: {chat_text}")

                            msg = json.dumps(
                                {
                                    "text": res_text,
                                    "speed": 1.2,
                                    "role": "byjk_female_康玥莹01",
                                    "sample_rate": 15000,
                                    "chunk_size": 4000,
                                },
                                ensure_ascii=False)
                            tts_client.send_message(msg)

                            for ac in action:
                                logging.info(f"执行动作: {ac}")
                                eval(ac)
                    else:
                        msg = json.dumps(
                            {"text": f"抱歉调用大模型错误，错误代码{chat_response.status_code}", "speed": 1.0,
                             "role": "byjk_female_康玥莹01",
                             "sample_rate": 16000},
                            ensure_ascii=False)
                        tts_client.send_message(msg)


    except KeyboardInterrupt:
        logging.info("录音被用户中断")

    logging.info("录音结束")
