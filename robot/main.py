# -*- coding: utf-8 -*-
import sys
import platform

system_type = platform.system()

if system_type == "Windows":
    sys.path.append("D:\\gopath\\src\\github.com\\TommyZihao\\tonypi")
elif system_type == "Linux":
    sys.path.append("/home/pi/tonypi")

import time
import queue
import logging
import threading
from robot.config.config import load_config
from robot.workers.task_chat import task_chat
from robot.workers.task_act import task_act
from robot.workers.task_classify import task_classify
from robot.workers.task_img import task_img
# from robot.workers.task_face import task_face
from robot.workers.task_camera import task_camera

if __name__ == "__main__":
    # 加载配置文件
    config_path = './config.yaml'
    config = load_config(config_path)

    # 配置日志级别
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')
    logging.info(f"Loaded config: {config}")

    chat_queue = queue.Queue()
    act_queue = queue.Queue()
    img_recognition_queue = queue.Queue()
    face_recognition_queue = queue.Queue()

    # 创建线程列表
    workers = []

    classify_worker = threading.Thread(
        target=task_classify,
        args=(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config),
        name="ClassifyWorker",
        daemon=True
    )
    workers.append(classify_worker)

    chat_worker = threading.Thread(
        target=task_chat,
        args=(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config),
        name="ChatWorker",
        daemon=True
    )
    workers.append(chat_worker)

    act_worker = threading.Thread(
        target=task_act,
        args=(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config),
        name="ActWorker",
        daemon=True
    )
    workers.append(act_worker)

    camera_worker = threading.Thread(
        target=task_camera,
        args=(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config),
        name="CameraWorker",
        daemon=True
    )
    workers.append(camera_worker)

    img_worker = threading.Thread(
        target=task_img,
        args=(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config),
        name="ImgWorker",
        daemon=True
    )
    workers.append(img_worker)

    # face_worker = threading.Thread(
    #     target=task_face,
    #     args=(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config),
    #     name="FaceWorker",
    #     daemon=True
    # )
    # workers.append(face_worker)

    # 启动所有线程
    for worker in workers:
        worker.start()
        logging.info(f"Started worker: {worker.name}")

    # 主线程阻塞不退出
    try:
        while True:
            time.sleep(1)
            # 可在此添加心跳检测逻辑
    except KeyboardInterrupt:
        logging.warning("Main thread received KeyboardInterrupt")
    finally:
        # 清理资源（daemon=True 时可省略）
        for worker in workers:
            if worker.is_alive():
                worker.join(timeout=5)
        logging.info("All workers stopped")
