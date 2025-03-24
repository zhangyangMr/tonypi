# -*- coding: utf-8 -*-
import logging
import time
from robot.img_understand.baidu_img import BaiduImgs
from robot.tts.text_to_wav_file import text_to_wav_file


def task_img(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config):
    logging.info("task_img workers start...")
    img_typ = config.get('img_understand')['img_understand_type']
    token_url = config.get('img_understand')['baidu']['token_url']
    api_key = config.get('img_understand')['baidu']['api_key']
    api_url = config.get('img_understand')['baidu']['api_url']
    secret_key = config.get('img_understand')['baidu']['secret_key']
    baidu_imgs = BaiduImgs(token_url, api_url, api_key, secret_key)

    tts_base_url = config.get('tts')['bobfintech']['tts_base_url']

    while True:
        time.sleep(0.1)

        if img_recognition_queue.empty():
            continue

        asr_msg_text = img_recognition_queue.get()

        # 将需要识别的图片发给百度图片理解接口，发起任务
        task_id = baidu_imgs.request(asr_msg_text)
        time.sleep(5)

        if task_id is not None:
            desc = baidu_imgs.result(task_id)
            if desc is not None:
                # tts_client.send_message(desc)
                text_to_wav_file(tts_base_url, desc)
            else:
                # tts_client.send_message("无法识别")
                text_to_wav_file(tts_base_url, "无法识别")
        else:
            # tts_client.send_message("百度AI图像接口错误")
            text_to_wav_file(tts_base_url, "百度AI图像接口错误")
