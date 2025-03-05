#!/usr/bin/python3
# coding=utf8
import hiwonder.Camera as Camera
import logging
import time
import cv2
import threading

from cfg_utils import read_llm_cfg, reflect_json_2_class
from llm import init_maasapi_llm_chain
from llm_config import LLMConfig, MaasApiConf
from text_to_sound import TTSClient
from baidu_img import request, result
from text_to_wav_file import text_to_wav_file

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

global tts_client


def recognition(host, question):
    task_id = request(question)
    time.sleep(5)
    if task_id is not None:
        desc = result(task_id)
        if desc is not None:
            # tts_client.send_message(desc)
            text_to_wav_file(host, desc)
        else:
            # tts_client.send_message("无法识别")
            text_to_wav_file(host, "无法识别")
    else:
        # tts_client.send_message("百度AI图像接口错误")
        text_to_wav_file(host, "百度AI图像接口错误")


def call_camera():
    my_camera = Camera.Camera()
    my_camera.camera_open()

    while True:
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()
            # frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # 畸变矫正(distortion correction)
            cv2.imshow('Frame', frame)
            cv2.imwrite("frame.jpg", frame)
            key = cv2.waitKey(500)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()


def start_camera():
    camera_thread = threading.Thread(target=call_camera)
    camera_thread.start()
