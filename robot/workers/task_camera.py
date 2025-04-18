# -*- coding: utf-8 -*-
import platform

system_type = platform.system()
if system_type == "Linux":
    import hiwonder.Camera as Camera
import logging
import cv2
import time


def task_camera(chat_queue, act_queue, img_recognition_queue, face_recognition_queue, config):
    logging.info("task_camera workers start...")
    # 打开摄像头
    if system_type == "Linux":
        my_camera = Camera.Camera()
        my_camera.camera_open()
    else:
        my_camera = cv2.VideoCapture(0)

    while True:
        time.sleep(0.01)
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()

            # 将抓取的图像写入文件
            cv2.imwrite("frame.jpg", frame)

            # 在窗口中显示视频流
            cv2.imshow("Camera Video", frame)

            # # frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # 畸变矫正(distortion correction)
            # cv2.imshow('Frame', frame)
            key = cv2.waitKey(33)
            if key == 27:
                break
        else:
            time.sleep(0.01)

    if system_type == "Linux":
        my_camera.camera_close()
    else:
        my_camera.release()

    cv2.destroyAllWindows()
