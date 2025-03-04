import time

import cv2
import numpy as np

# 加载 YOLOv3 模型
net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

# 加载类别名称
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# 初始化视频流
cap = cv2.VideoCapture(0)  # 使用摄像头

while True:
    ret, frame = cap.read()
    height, width, _ = frame.shape

    # 创建输入 blob
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(net.getUnconnectedOutLayersNames())

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # 绘制边界框
    for i in range(len(boxes)):
        x, y, w, h = boxes[i]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{classes[class_ids[i]]} {int(confidences[i] * 100)}%", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow("Object Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
