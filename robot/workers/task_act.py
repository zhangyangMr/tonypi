# -*- coding: utf-8 -*-
import logging
import time
import json
import platform

from robot.llm.llm_factory import ModelFactory
from robot.utils.utils import deal_maas_response
from robot.tts.text_to_wav_file import text_to_wav_file
from robot.workers.task_camera import system_type

system_type = platform.system()

if system_type == "Linux":
    from robot.utils.utils_robot import *


def task_act(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config):
    logging.info("task_act workers start...")

    # 初始化大模型
    llm_type = config.get('llm')['llm_type']
    llm_url = config.get('llm')['maas']['maas_api_url']
    robot_api_key = config.get('llm')['maas']['maas_api_key']['robot']
    llm_factory = ModelFactory.get_model(llm_type, llm_url, robot_api_key)

    tts_base_url = config.get('tts')['bobfintech']['tts_base_url']

    while True:
        time.sleep(0.1)

        if act_queue.empty():
            continue

        # 和大模型对话
        asr_msg_text = act_queue.get()
        robot_response = llm_factory.chat(asr_msg_text, streaming=False)
        robot_result = deal_maas_response(robot_response)
        logging.info(f"task_act robot_result: {robot_result}")

        robot_result_text = robot_result["text"]
        robot_result_text = robot_result_text.replace("'", '"')
        robot_text_json = json.loads(robot_result_text)

        robot_action = robot_text_json["action"]
        robot_text = robot_text_json["response"]

        # 播放声音
        text_to_wav_file(tts_base_url, robot_text)

        # 执行动作
        for ac in robot_action:
            logging.info(f"执行动作: {ac}")
            if system_type == "Linux":
                eval(ac)

        act_queue.task_done()
