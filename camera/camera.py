#!/usr/bin/python3
# coding=utf8
import hiwonder.Camera as Camera
import logging
import time
import cv2

from cfg_utils import read_llm_cfg, reflect_json_2_class
from llm import init_maasapi_llm_chain
from llm_config import LLMConfig, MaasApiConf
from text_to_sound import TTSClient
from baidu_img import request, result

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

global tts_client

def recognition():
    task_id = request()
    time.sleep(5)
    if task_id is not None:
        desc = result(task_id)
        if desc is not None:
            tts_client.send_message(desc)
        else:
            tts_client.send_message("无法识别")
    else:
        tts_client.send_message("百度AI图像接口错误")


if __name__ == '__main__':
    cfg_path = "./llm_conf.yaml"
    logging.info('start recognition')
    llm_cfg = read_llm_cfg(cfg_path)
    model_detail_config = reflect_json_2_class(llm_cfg, LLMConfig)
    logging.info(f"model_detail_config: {model_detail_config}")

    maas_api_cfg = reflect_json_2_class(model_detail_config.maas_api_conf, MaasApiConf)
    maas_chain = init_maasapi_llm_chain(model_detail_config, "common_use")

    # 初始化TTS
    tts_uri = maas_api_cfg.tts_url
    tts_client = TTSClient(tts_uri)
    tts_client.start()
    tts_client.send_message("启动中")

    my_camera = Camera.Camera()
    my_camera.camera_open()

    while True:
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()
            # frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # 畸变矫正(distortion correction)
            cv2.imshow('Frame', frame)
            cv2.imwrite("frame.jpg", frame)
            recognition()
            # task_id = request()
            # time.sleep(5)
            # if task_id is not None:
            #     desc = result(task_id)
            #     if desc is not None:
            #         tts_client.send_message(desc)
            #     else:
            #         tts_client.send_message("无法识别")
            # else:
            #     tts_client.send_message("百度AI图像接口错误")
            key = cv2.waitKey(10000)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()
