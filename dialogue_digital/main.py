# -*- coding: utf-8 -*-
import threading
import time

import pyaudio
import logging
import json
import queue

from sound_to_text import AsrOnline
from text_to_sound import TTSClient

from cfg_utils import read_llm_cfg, reflect_json_2_class
from llm_config import LLMConfig, MaasApiConf
from llm import init_maasapi_llm_chain
from utils import starts_with_chinese_pinyin
from text_to_wav_file import text_to_wav_file

# from utils_robot import *

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')


def deal_response(response):
    """对大模型返回结果进行统一数据处理"""
    if response.status_code == 200:
        chat_result = response.json()
        if chat_result.get("code") == 200:
            return chat_result.get("data")
        else:
            tmp_text = f"抱歉调用大模型错误，错误代码{response.status_code}"
            logging.info(f"deal_response tmp text: {tmp_text}")
    else:
        tmp_text = f"抱歉调用大模型错误，错误代码{response.status_code}"
        logging.info(f"deal_response tmp text: {tmp_text}")


def chat_maas(robot_maas_chain, chat_maas_chain, classify_maas_chain, tts_client, tts_base_url, asr_msg, tts_queue):
    """和大模型进行交互"""

    # 对外界语音进行分类，是动作类action，还是聊天类chat
    classify_response = classify_maas_chain.chat(asr_msg)
    classify_result = deal_response(classify_response)
    logging.info(f"classify_result: {classify_result}")

    classify_result_text = classify_result["text"]
    classify_text_list = json.loads(classify_result_text)

    for classify_text in classify_text_list:
        if classify_text == "chat":
            chat_response = chat_maas_chain.chat(asr_msg)
            chat_result = deal_response(chat_response)
            logging.info(f"chat_result: {chat_result}")

            chat_result_text = chat_result["text"]
            logging.info(f"chat_result_text: {chat_result_text}; type: {type(chat_result_text)}")
            # tts_client.send_message(chat_result_text)
            text_to_wav_file(tts_base_url, chat_result_text)
        else:
            # 获取机器人动作指令
            robot_response = robot_maas_chain.chat(asr_msg, False)
            robot_result = deal_response(robot_response)
            logging.info(f"robot_result: {robot_result}")

            robot_result_text = robot_result["text"]
            robot_result_text = robot_result_text.replace("'", '"')
            robot_text_json = json.loads(robot_result_text)

            robot_action = robot_text_json["action"]
            robot_text = robot_text_json["response"]
            logging.info(f"robot_text: {robot_text}")
            # tts_client.send_message(robot_text)
            text_to_wav_file(tts_base_url, robot_text)

            for ac in robot_action:
                logging.info(f"执行动作: {ac}")
                # eval(ac)
    tts_queue.get()
    tts_queue.task_done()


if __name__ == '__main__':
    cfg_path = "./llm_conf.yaml"

    # 初始化MaaS大模型
    llm_cfg = read_llm_cfg(cfg_path)
    model_detail_config = reflect_json_2_class(llm_cfg, LLMConfig)
    logging.info(f"model_detail_config: {model_detail_config}")

    maas_api_cfg = reflect_json_2_class(model_detail_config.maas_api_conf, MaasApiConf)

    # 初始化大模型client
    classify_maas_chain = init_maasapi_llm_chain(model_detail_config, "classify")
    robot_maas_chain = init_maasapi_llm_chain(model_detail_config, "robot")
    chat_maas_chain = init_maasapi_llm_chain(model_detail_config, "chat")

    # 创建一个队列，控制tts发送和接收数据一一对应
    tts_queue = queue.Queue(maxsize=1)

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
        uri=maas_api_cfg.asr_url,
        is_ssl=False,
        chunk_size="-1, 10, 5",
        mode="2pass"
    )

    # 初始化TTS
    tts_uri = maas_api_cfg.tts_url
    tts_client = TTSClient(tts_uri, tts_queue)
    tts_client.start()

    try:
        while True:
            time.sleep(0.01)
            tts_queue.put(1)
            # 从麦克风持续读取数据
            # logging.info("开始从麦克风读取音频数据...")
            data = input_stream.read(CHUNK, exception_on_overflow=False)

            # 重连asr_client
            if asr_client.websocket is None:
                # 初始化asr
                asr_client = AsrOnline(
                    uri=maas_api_cfg.asr_url,
                    is_ssl=False,
                    chunk_size="-1, 10, 5",
                    mode="2pass"
                )
                asr_msg = asr_client.feed_chunk(data, wait_time=0.01)
            else:
                asr_msg = asr_client.feed_chunk(data, wait_time=0.01)

            if len(asr_msg) > 0:
                logging.info(f"asr_msg: {asr_msg}")
                if starts_with_chinese_pinyin(asr_msg["text"], "小宝"):
                    chat_maas(robot_maas_chain, chat_maas_chain, classify_maas_chain, tts_client,
                              maas_api_cfg.tts_base_url, asr_msg["text"], tts_queue)
                else:
                    tts_queue.get()
                    tts_queue.task_done()
            else:
                tts_queue.get()
                tts_queue.task_done()

    except KeyboardInterrupt:
        logging.info("录音被用户中断")

    logging.info("录音结束")
