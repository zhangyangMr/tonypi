# -*- coding: utf-8 -*-
import time

import dlib
import cv2
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
import hiwonder.Camera as Camera
import logging
import csv

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

person_names = {
    "huge": "胡歌",
    "huzong": "胡总",
    "jingtian": "景甜",
    "liangchaowei": "梁朝伟",
    "liudehua": "刘德华",
    "liuyifei": "刘亦菲",
    "nini": "倪妮",
    "ruijie": "蕊姐",
    "shuji": "书记",
    "wanqian": "万茜",
    "yudashi": "于大师",
    "zhangjike": "张继科",
    "zhangyang": "张洋"
}

swapped_person_names = {value: key for key, value in person_names.items()}

# 初始化 dlib 的人脸检测器、关键点检测器和特征提取器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")


# 加载已知人脸数据库
def load_known_faces(folder_path):
    known_faces = []
    known_labels = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(folder_path, filename)
            img = dlib.load_rgb_image(img_path)
            faces = detector(img)
            if faces:
                shape = predictor(img, faces[0])
                face_descriptor = face_rec_model.compute_face_descriptor(img, shape)
                known_faces.append(face_descriptor)
                known_labels.append(filename.split('.')[0])
    return np.array(known_faces), known_labels


# 加载已知人脸特征
def load_known_faces_from_csv(csv_path):
    with open(csv_path, "r", encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        known_faces = []
        known_names = []
        for row in reader:
            known_names.append(row[0])
            known_faces.append(np.array(row[1:], dtype=np.float64))
    return np.array(known_faces), known_names


# 计算人脸特征
def get_face_descriptor(img):
    faces = detector(img)
    if not faces:
        return None
    shape = predictor(img, faces[0])
    face_descriptor = face_rec_model.compute_face_descriptor(img, shape)
    return face_descriptor


# 人脸识别函数
def recognize_face(frame, known_faces, known_labels, threshold=0.6):
    # img = dlib.load_rgb_image(image_path)
    face_descriptor = get_face_descriptor(frame)
    if face_descriptor is None:
        return "No face detected"

    # 将特征向量转换为二维数组
    face_descriptor = np.array([face_descriptor])
    known_faces = np.array(known_faces)

    # 计算相似度
    similarities = cosine_similarity(face_descriptor, known_faces)[0]
    max_similarity = max(similarities)
    if max_similarity > threshold:
        index = np.argmax(similarities)
        return known_labels[index]
    else:
        return "Unknown"


if __name__ == "__main__":
    # 加载已知人脸数据库
    known_faces, known_labels = load_known_faces_from_csv("./features.csv")

    # 打开摄像头
    logging.info("打开摄像头")
    my_camera = Camera.Camera()
    my_camera.camera_open()
    while True:
        time.sleep(0.1)
        logging.info("读取摄像头数据")
        ret, frame = my_camera.read()
        if ret:
            result = recognize_face(frame, known_faces, known_labels)
            print(f"Recognized as: {result}")
            # 在窗口中显示识别结果
            if result != "Unknown":
                print(f"Recognized: {result}")
                cv2.putText(frame, f"Welcome, {result}!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unknown Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 显示视频流
            cv2.imshow("Face Recognition", frame)

            if cv2.waitKey(33) & 0xFF == 27:  # 按 Esc 退出
                break
        else:
            time.sleep(0.1)

    my_camera.camera_close()
    cv2.destroyAllWindows()
