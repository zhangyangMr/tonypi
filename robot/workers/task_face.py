# -*- coding: utf-8 -*-
import logging
import time

import cv2
import threading

from robot.face_recognition.face_dlib_real import recognize_face, load_known_faces_from_csv, swapped_person_names
from robot.llm.llm_factory import ModelFactory
from robot.utils.utils import deal_maas_response
from robot.tts.text_to_wav_file import text_to_wav_file


def task_face(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config):
    logging.info("task_face workers start...")

    # # 加载已知人脸数据
    # known_faces, known_labels = load_known_faces_from_csv("./features.csv")
    #
    # # 初始化大模型
    # llm_type = config.get('llm')['llm_type']
    # llm_url = config.get('llm')['maas']['maas_api_url']
    # chat_api_key = config.get('llm')['maas']['maas_api_key']['chat']
    # llm_factory = ModelFactory.get_model(llm_type, llm_url, chat_api_key)
    #
    # tts_base_url = config.get('tts')['bobfintech']['tts_base_url']

    stop_event = threading.Event()
    face_task = threading.Thread(
        target=woker_face,
        args=(config, stop_event),
        name="face_tak",
        daemon=True  # 设为守护线程随主线程退出
    )

    while True:
        time.sleep(0.1)

        if face_recognition_queue.empty():
            continue

        asr_msg_text = face_recognition_queue.get()

        if asr_msg_text == "open":
            if face_task.is_alive():
                continue
            else:
                face_task.start()
        else:
            stop_event.set()
            face_task.join()

        # if asr_msg_text == "开启":
        #     while True:
        #         frame = cv2.imread("./frame.jpg")
        #
        #         result = recognize_face(frame, known_faces, known_labels)
        #         # 在窗口中显示识别结果
        #         if result != "Unknown" and result != "No face detected":
        #             logging.info(f"Recognized: {swapped_person_names.get(result)}")
        #             cv2.putText(frame, f"Welcome, {swapped_person_names.get(result)}!", (50, 50),
        #                         cv2.FONT_HERSHEY_SIMPLEX,
        #                         1, (0, 255, 0), 2)
        #
        #             chat_response = llm_factory.chat(f"给{result}打招呼")
        #             chat_result = deal_maas_response(chat_response)
        #             logging.info(f"task_face chat_result: {chat_result}")
        #
        #             chat_result_text = chat_result["text"]
        #             text_to_wav_file(tts_base_url, chat_result_text)
        #         else:
        #             cv2.putText(frame, "Unknown Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        #
        #         cv2.imshow("Face Recognition", frame)
        #
        # face_recognition_queue.task_done()


def woker_face(config, stop_event):
    # 加载已知人脸数据
    known_faces, known_labels = load_known_faces_from_csv("./features.csv")

    # 初始化大模型
    llm_type = config.get('llm')['llm_type']
    llm_url = config.get('llm')['maas']['maas_api_url']
    chat_api_key = config.get('llm')['maas']['maas_api_key']['chat']
    llm_factory = ModelFactory.get_model(llm_type, llm_url, chat_api_key)

    tts_base_url = config.get('tts')['bobfintech']['tts_base_url']

    while not stop_event.is_set():
        time.sleep(0.1)
        frame = cv2.imread("./frame.jpg")

        result = recognize_face(frame, known_faces, known_labels)
        # 在窗口中显示识别结果
        if result != "Unknown" and result != "No face detected":
            logging.info(f"Recognized: {swapped_person_names.get(result)}")
            cv2.putText(frame, f"Welcome, {swapped_person_names.get(result)}!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            chat_response = llm_factory.chat(f"给{result}打招呼")
            chat_result = deal_maas_response(chat_response)
            logging.info(f"task_face chat_result: {chat_result}")

            chat_result_text = chat_result["text"]
            text_to_wav_file(tts_base_url, chat_result_text)
        else:
            cv2.putText(frame, "Unknown Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Face Recognition", frame)
