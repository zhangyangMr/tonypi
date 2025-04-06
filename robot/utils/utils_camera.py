# -*- coding: utf-8 -*-
import logging
import platform
import numpy as np
import cv2
import csv
import dlib
from PIL import Image, ImageDraw, ImageFont
from sklearn.metrics.pairwise import cosine_similarity

# 初始化 dlib 的人脸检测器、关键点检测器和特征提取器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./dependence/shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("./dependence/dlib_face_recognition_resnet_model_v1.dat")

def put_text_2_img(frame, text):
    """
    将文字写入图像frame。

    :param text: 需要写入的文字信息

    :return frame: 返回写入文字的图像frame信息
    """

    # 将 OpenCV 图像转换为 PIL 格式
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # 创建绘图对象
    draw = ImageDraw.Draw(frame_pil)

    system_type = platform.system()

    # 设置字体（需要指定支持中文的字体文件路径）
    if system_type == "Windows":
        font_path = "simsun.ttc"  # 例如宋体字体文件
    elif system_type == "Linux":
        font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    else:
        font_path = "simsun.ttc"

    font = ImageFont.truetype(font_path, 30)

    # 添加中文文字
    draw.text((50, 50), text, font=font, fill=(0, 0, 255))

    # 将 PIL 图像转换回 OpenCV 格式
    frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    return frame

def load_known_faces_from_csv(csv_path):
    """
    加载已知人脸特征。

    :param csv_path: 人脸特征csv文件

    :return known_faces: 返回csv文件全部人脸特征
    :return known_names: 返回对应全部人名
    """
    with open(csv_path, "r", encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        known_faces = []
        known_names = []
        for row in reader:
            known_names.append(row[0])
            known_faces.append(np.array(row[1:], dtype=np.float64))
    return np.array(known_faces), known_names


def get_face_descriptor(img):
    """
    计算人脸特征。

    :param img: 人脸图片

    :return face_descriptor: 返回人脸特征
    """
    faces = detector(img)
    if not faces:
        return None
    shape = predictor(img, faces[0])
    face_descriptor = face_rec_model.compute_face_descriptor(img, shape)
    return face_descriptor


def recognize_face(frame, known_faces, known_labels, threshold=0.6):
    """
    人脸识别函数。

    :param frame: 人脸图片信息
    :param known_faces: 已知全部人脸信息
    :param known_labels: 已知全部人脸标签
    :param threshold: 期望精度值

    :return known_label: 返回识别出的对应人名
    """
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

def is_face_centered(face_box, frame_width, frame_height, tolerance=0.3):
    """
    判断人脸是否在画面中心，并返回偏差方向
    :param face_box: 人脸框坐标 (x, y, w, h)
    :param frame_width: 帧宽度
    :param frame_height: 帧高度
    :param tolerance: 容忍度，允许一定误差
    :return: 是否在中心, 偏差方向
    """
    (x, y, w, h) = face_box
    face_center_x = x + w / 2
    face_center_y = y + h / 2

    center_x = frame_width / 2
    center_y = frame_height / 2

    is_centered = (abs(face_center_x - center_x) <= frame_width * tolerance / 2) and \
                  (abs(face_center_y - center_y) <= frame_height * tolerance / 2)

    direction = ""
    if face_center_x < center_x - frame_width * tolerance / 2:
        direction += "右"
    elif face_center_x > center_x + frame_width * tolerance / 2:
        direction += "左"

    if face_center_y < center_y - frame_height * tolerance / 2:
        direction += "下"
    elif face_center_y > center_y + frame_height * tolerance / 2:
        direction += "上"

    return is_centered, direction


def detect_faces(frame, face_cascade):
    """
    检测人脸并返回人脸框
    :param frame: 视频帧
    :param face_cascade: 人脸检测分类器
    :return: 人脸框列表
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces