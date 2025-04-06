# -*- coding: utf-8 -*-
import logging
import cv2
import csv
import dlib
import platform
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.metrics.pairwise import cosine_similarity
from robot.config.config import *
from robot.llm.llm_factory import ModelFactory
from robot.utils.utils import deal_maas_response
from robot.tts.text_to_wav_file import text_to_wav_file
from robot.utils.utils_camera import recognize_face, load_known_faces_from_csv, detect_faces, is_face_centered, \
    put_text_2_img

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

system_type = platform.system()
if system_type == "Linux":
    import hiwonder.Camera as Camera

if __name__ == "__main__":
    # 加载已知人脸数据库
    known_faces, known_labels = load_known_faces_from_csv("./dependence/features.csv")

    config_path = './config.yaml'
    config = load_config(config_path)

    # 初始化大模型
    llm_type = config.get('llm')['llm_type']
    llm_url = config.get('llm')['maas']['maas_api_url']
    chat_api_key = config.get('llm')['maas']['maas_api_key']['chat']
    llm_factory = ModelFactory.get_model(llm_type, llm_url, chat_api_key)

    tts_base_url = config.get('tts')['bobfintech']['tts_base_url']

    # 打开摄像头
    logging.info("打开摄像头")
    # if system_type == "Linux":
    #     my_camera = Camera.Camera()
    #     my_camera.camera_open()
    # else:
    #     my_camera = cv2.VideoCapture(0)

    while True:
        time.sleep(0.1)
        logging.info("读取摄像头数据")
        img = cv2.imread("./frame.jpg")
        # ret, img= my_camera.read()
        if img is not None:
            frame = img.copy()
            result = recognize_face(frame, known_faces, known_labels)
            # 在窗口中显示识别结果
            if result != "Unknown" and result != "No face detected":
                logging.info(f"Face Recognized result: {result}")
                frame = put_text_2_img(frame, f"Welcome, {result}!")
                cv2.imshow("Face Recognition", frame)

                chat_response = llm_factory.chat(f"给{result}打招呼")
                chat_result = deal_maas_response(chat_response)
                logging.info(f"task_face chat_result: {chat_result}")

                chat_result_text = chat_result["text"]
                text_to_wav_file(tts_base_url, chat_result_text)
            else:
                frame = put_text_2_img(frame, "Unknown Person")
                cv2.imshow("Face Recognition", frame)

            # 显示视频流

            if cv2.waitKey(33) & 0xFF == 27:  # 按 Esc 退出
                break
        else:
            time.sleep(0.1)

    # if system_type == "Linux":
    #     my_camera.camera_close()
    # else:
    #     my_camera.release()

    cv2.destroyAllWindows()
