import dlib
import cv2
import os
import csv
import numpy as np
from skimage import io
from pathlib import Path
import logging

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

# 初始化 dlib 模型
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")


# 提取单张图片的 128D 特征
def return_128d_features(path_img):
    img_rd = io.imread(path_img)
    img_gray = cv2.cvtColor(img_rd, cv2.COLOR_BGR2RGB)
    faces = detector(img_gray, 1)

    if len(faces) != 0:
        shape = predictor(img_gray, faces[0])
        face_descriptor = face_rec.compute_face_descriptor(img_gray, shape)
    else:
        face_descriptor = None
    return face_descriptor


# 提取某人所有图片的特征均值
def return_features_mean_personX(path_faces_personX):
    features_list_personX = []
    photos_list = os.listdir(path_faces_personX)

    for i in range(len(photos_list)):
        features_128d = return_128d_features(os.path.join(path_faces_personX, photos_list[i]))
        if features_128d is not None:
            features_list_personX.append(features_128d)

    if features_list_personX:
        features_mean_personX = np.array(features_list_personX).mean(axis=0)
    else:
        features_mean_personX = None
    return features_mean_personX


# 保存特征到 CSV 文件
def save_features_to_csv(features, names, csv_path):
    with open(csv_path, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(names)):
            writer.writerow([names[i]] + list(features[i]))


# 加载已知人脸单张照片特征
def load_known_faces(folder_path):
    known_faces = []
    known_labels = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(folder_path, filename)
            img_path = img_path.replace("\\", "/")
            img_rd = io.imread(img_path)
            img = cv2.cvtColor(img_rd, cv2.COLOR_BGR2RGB)
            # img = dlib.load_rgb_image(img_path)
            faces = detector(img)
            if faces:
                shape = predictor(img, faces[0])
                face_descriptor = face_rec.compute_face_descriptor(img, shape)
                known_faces.append(face_descriptor)

                name = filename.split('.')[0]
                # logging.info(f"name: {name}; person_names.get(name): {person_names.get(name)}")
                # known_labels.append(person_names.get(name))
                logging.info(f"name: {name}")
                known_labels.append(name)
    return np.array(known_faces), known_labels


# 加载一人多张照片特征数据
def load_known_faces_with_persons():
    path_images_from_camera = r"./images_with_persons"
    people = os.listdir(path_images_from_camera)
    # people.sort()
    features = []
    names = []

    for person in people:
        logging.info(f"Processing {person}")
        person_path=os.path.join(path_images_from_camera, person)
        logging.info(f"Processing path: {person_path}")
        features_mean_personX = return_features_mean_personX(person_path)
        if features_mean_personX is not None:
            features.append(features_mean_personX)
            names.append(person)

    save_features_to_csv(features, names, "features.csv")
    logging.info("Features saved to features.csv")


def load_known_faces_with_one_person():
    # 加载已知人脸数据库
    known_faces, known_labels = load_known_faces("./images_one_person")
    save_features_to_csv(known_faces, known_labels, "features.csv")


if __name__ == "__main__":
    load_known_faces_with_one_person()
    # load_known_faces_with_persons()
#