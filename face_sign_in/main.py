# -*- coding: utf-8 -*-
import logging
import time
import platform
from db import *
from face import *
from text_to_wav_file import text_to_wav_file
from utils import load_config

system_type = platform.system()
print(f"当前操作系统为：{system_type}")

if system_type == "Linux":
    import hiwonder.Camera as Camera


def face_recognition(frame, known_faces, known_labels, conn, threshold=0.6):
    result = recognize_face(frame, known_faces, known_labels)
    # 在窗口中显示识别结果
    if result != "Unknown" and result != "No face detected":
        # 查询人员是否已签到
        sign_in_record = query_sign_in_record(conn, result)

        sign_in_time_str = sign_in_record[4]
        update_time_str = sign_in_record[5]

        time_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        today_dir = datetime.now().strftime("%Y-%m-%d")

        play_text = ""
        display_text = ""
        log_text = ""

        if sign_in_record[2] == 1:
            # 获取签到记录,并更新数据库updated_time时间
            update_time = datetime.strptime(update_time_str, "%Y-%m-%d %H:%M:%S")  # 转换为 datetime 对象
            # 计算当前时间和签到记录更新时间差
            time_difference = current_time - update_time
            if time_difference > timedelta(seconds=5):
                play_text = f"{result}在{sign_in_time_str}已签到"
                update_text = f"更新时间{time_now_str}"
                log_text = f"{play_text},{update_text}"
                display_text = f"{play_text},\n{update_text}"

                update_sign_in_record_with_update_time(conn, result)
        else:
            play_text = f"{result}在{time_now_str}签到成功"
            log_text = display_text
            display_text = play_text

            # 将签到记录更新到数据库中
            update_sign_in_record(conn, result, 1)

        logging.info(log_text)
        frame = put_text_2_img(frame, display_text)
        cv2.imshow("Face Sign In", frame)

        img_dir = Path(f"./face_img/{today_dir}")
        if not img_dir.exists():
            img_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"目录{img_dir}创建成功")
        else:
            logging.info(f"目录{img_dir}已存在")

        img_path = Path(f"{img_dir}/{result}.jpg")
        # 将 BGR 图像转换为 RGB 图像
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        Image.fromarray(image_rgb).save(img_path)

        text_to_wav_file(play_text, tts_url)
    else:
        cv2.putText(frame, "Unknown Person", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Face Sign In", frame)


def call_camera(tts_url):
    """调取摄像头，进行人脸识别"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 创建sqlite数据库连接
    conn = create_database("sign_in_records")

    # 插入签到人员信息
    insert_csv_data(conn, "./features.csv")

    # 加载已知人脸数据库
    known_faces, known_labels = load_known_faces_from_csv("./features.csv")

    # 打开摄像头
    if system_type == "Linux":
        my_camera = Camera.Camera()
    else:
        my_camera = cv2.VideoCapture(0)

    while True:
        time.sleep(0.01)
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()

            faces = detect_faces(frame, face_cascade)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                is_centered, direction = is_face_centered((x, y, w, h), frame.shape[1], frame.shape[0])
                if is_centered:
                    # 人脸在中心，进行人脸识别
                    logging.info("Face is centered, performing recognition...")
                    face_recognition(frame, known_faces, known_labels, conn)
                    # 在这里添加人脸识别的代码
                else:
                    logging.info(f"Face is not centered. Move your face {direction}.")
                    text_to_wav_file(f"请将脸向{direction}移动到屏幕中央", tts_url)

            cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # 按 Esc 退出
            break

    if system_type == "Linux":
        my_camera.camera_close()
    elif system_type == "Windows":
        my_camera.release()

    cv2.destroyAllWindows()
    close_database(conn)


if __name__ == '__main__':
    # 加载配置文件
    config_path = './config.yaml'
    config = load_config(config_path)

    tts_url = config.get('tts')['base_url']

    # 配置日志级别
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')
    logging.info(f"Loaded config: {config}")

    logging.info("face sign in start")
    call_camera(tts_url)
