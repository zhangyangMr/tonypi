# -*- coding: utf-8 -*-
import pyaudio
import logging
import json
import queue
import logging
import time
from robot.config.config import load_config
from robot.stt.asr import AsrOnline
from robot.utils.utils import starts_with_chinese_pinyin, deal_maas_response
from robot.llm.llm_factory import ModelFactory


def task_classify(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config):
    logging.info("task_classify workers start...")

    # 打开音频
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
    asr_url = config.get('stt')['bobfintech']['asr_url']

    asr_client = AsrOnline(
        uri=asr_url,
        is_ssl=False,
        chunk_size="-1, 10, 5",
        mode="2pass"
    )

    # 初始化大模型
    llm_type = config.get('llm')['llm_type']
    llm_url = config.get('llm')['maas']['maas_api_url']
    classify_api_key = config.get('llm')['maas']['maas_api_key']['classify']
    llm_factory = ModelFactory.get_model(llm_type, llm_url, classify_api_key)

    try:
        while True:
            time.sleep(0.1)
            # 从麦克风持续读取数据
            data = input_stream.read(CHUNK, exception_on_overflow=False)

            # 重连asr_client
            if asr_client.websocket is None:
                # 初始化asr
                asr_client = AsrOnline(
                    uri=asr_url,
                    is_ssl=False,
                    chunk_size="-1, 10, 5",
                    mode="2pass"
                )
                asr_msg = asr_client.feed_chunk(data, wait_time=0.01)
            else:
                asr_msg = asr_client.feed_chunk(data, wait_time=0.01)

            if len(asr_msg) > 0:
                logging.debug(f"接收的音频 asr_msg: {asr_msg}")
                asr_msg_text = asr_msg["text"]
                if starts_with_chinese_pinyin(asr_msg_text, "小宝"):
                    classify_response = llm_factory.chat(asr_msg_text, streaming=False)
                    classify_result = deal_maas_response(classify_response)
                    logging.info(f"classify_result: {classify_result}")

                    classify_result_text = classify_result["text"]
                    classify_text_list = json.loads(classify_result_text)
                    for classify_text in classify_text_list:
                        if classify_text == "action":
                            logging.debug(f"act : {asr_msg_text}")
                            act_queue.put(asr_msg_text)
                        elif classify_text == "img":
                            logging.debug(f"img : {asr_msg_text}")
                            img_recognition_queue.put(asr_msg_text)
                        elif classify_text == "face":
                            logging.debug(f"face: {asr_msg_text}")
                            face_recognition_queue.put(asr_msg_text)
                        else:
                            logging.debug(f"chat: {asr_msg_text}")
                            chat_queue.put(asr_msg_text)
            #     else:
            #         tts_queue.get()
            #         tts_queue.task_done()
            # else:
            #     tts_queue.get()
            #     tts_queue.task_done()

    except KeyboardInterrupt:
        logging.info("录音被用户中断")

    logging.info("录音结束")
