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
from face_dlib_real import load_known_faces_from_csv, recognize_face, swapped_person_names

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


def call_camera(model_detail_config, maas_api_cfg):
    # 初始化大模型
    chat_maas_chain = init_maasapi_llm_chain(model_detail_config, "chat")
    tts_base_url = maas_api_cfg.tts_base_url

    # 加载已知人脸数据库
    known_faces, known_labels = load_known_faces_from_csv("./features.csv")

    # 打开摄像头
    my_camera = Camera.Camera()
    my_camera.camera_open()

    while True:
        time.sleep(0.01)
        ret, img = my_camera.read()
        if ret:
            time.sleep(0.01)
            frame = img.copy()
            cv2.imwrite("frame.jpg", frame)
            result = recognize_face(frame, known_faces, known_labels)
            # logging.info(f"Recognized as: {result}")
            # 在窗口中显示识别结果
            if result != "Unknown" and result != "No face detected":
                logging.info(f"Recognized: {swapped_person_names.get(result)}")

                chat_response = chat_maas_chain.chat(f"给{result}打招呼")
                chat_result = deal_response(chat_response)
                logging.info(f"chat_result: {chat_result}")

                chat_result_text = chat_result["text"]
                logging.info(f"chat_result_text: {chat_result_text}; type: {type(chat_result_text)}")
                text_to_wav_file(tts_base_url, chat_result_text)

                cv2.putText(frame, f"Welcome, {swapped_person_names.get(result)}!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unknown Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 显示视频流
            cv2.imshow("Face Recognition", frame)

            # # frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # 畸变矫正(distortion correction)
            # cv2.imshow('Frame', frame)
            key = cv2.waitKey(33)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()


def start_camera(model_detail_config, maas_api_cfg):
    camera_thread = threading.Thread(target=call_camera, args=(model_detail_config, maas_api_cfg))
    camera_thread.start()
