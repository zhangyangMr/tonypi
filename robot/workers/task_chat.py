# -*- coding: utf-8 -*-
import logging
import time

from robot.llm.llm_factory import ModelFactory
from robot.utils.utils import deal_maas_response
from robot.tts.text_to_wav_file import text_to_wav_file


def task_chat(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config):
    logging.info("task_chat workers start...")

    # 初始化大模型
    llm_type = config.get('llm')['llm_type']
    llm_url = config.get('llm')['maas']['maas_api_url']
    chat_api_key = config.get('llm')['maas']['maas_api_key']['chat']
    llm_factory = ModelFactory.get_model(llm_type, llm_url, chat_api_key)

    tts_base_url = config.get('tts')['bobfintech']['tts_base_url']

    while True:
        time.sleep(0.1)

        if chat_queue.empty():
            continue

        # 和大模型对话
        asr_msg_text = chat_queue.get()
        chat_response = llm_factory.chat(asr_msg_text, streaming=False)
        chat_result = deal_maas_response(chat_response)
        logging.info(f"task_chat chat_result: {chat_result}")

        # 播放声音
        chat_result_text = chat_result["text"]
        text_to_wav_file(tts_base_url, chat_result_text)
