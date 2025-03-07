#!/usr/bin/python3
# coding=utf8
import sys
import os
import cv2
import math
import time
import numpy as np

import hiwonder.Camera as Camera
import hiwonder.yaml_handle as yaml_handle

# 颜色跟踪(color tracking)
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


__target_color = ('red')

def setLABValue(lab_value):
    global lab_data
    global __target_color
    
    __target_color = (lab_value[0]['color'], )
    lab_data[__target_color[0]]['min'][0] = lab_value[0]['min'][0]
    lab_data[__target_color[0]]['min'][1] = lab_value[0]['min'][1]
    lab_data[__target_color[0]]['min'][2] = lab_value[0]['min'][2]
    lab_data[__target_color[0]]['max'][0] = lab_value[0]['max'][0]
    lab_data[__target_color[0]]['max'][1] = lab_value[0]['max'][1]
    lab_data[__target_color[0]]['max'][2] = lab_value[0]['max'][2]
    
    return (True, (), 'SetLABValue')

def getLABValue():
    _lab_value = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    return (True, (_lab_value, ))

def saveLABValue(color):
    yaml_handle.save_yaml_data(lab_data, yaml_handle.lab_file_path)
    
    return (True, (), 'SaveLABValue')



lab_data = None
servo_data = None
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)


# 变量重置(variable reset)
def reset():
    global __target_color
       
    __target_color = ()

# app初始化调用(app initialization calling)
def init():
    print("lab_adjust Init")
    load_config()
    reset()

__isRunning = False
# app开始玩法调用(app start program calling)
def start():
    global __isRunning
    __isRunning = True
    print("lab_adjust Start")

# app停止玩法调用(app stop program calling)
def stop():
    global __isRunning
    __isRunning = False
    reset()
    print("lab_adjust Stop")

# app退出玩法调用(app exit program calling)
def exit():
    global __isRunning
    __isRunning = False
    print("lab_adjust Exit")

def run(img):  
    img_copy = img.copy()
    
    if not __isRunning or __target_color == ():
        return img
    
    frame_gb = cv2.GaussianBlur(img_copy, (3, 3), 3)   
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间(convert the image to LAB space)
    
    for i in lab_data:
        if i in __target_color:
            frame_mask = cv2.inRange(frame_lab,
                                         (lab_data[i]['min'][0],
                                          lab_data[i]['min'][1],
                                          lab_data[i]['min'][2]),
                                         (lab_data[i]['max'][0],
                                          lab_data[i]['max'][1],
                                          lab_data[i]['max'][2]))  #对原图像和掩模进行位运算(perform bitwise operation to original image and mask)
            eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  #腐蚀(corrosion)
            dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) #膨胀(dilation)
            frame_bgr = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
            img = frame_bgr
            
    return img

if __name__ == '__main__': 

    init()
    start()
   
    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
    if open_once:
        my_camera = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
    else:
        my_camera = Camera.Camera()
        my_camera.camera_open()        
    while True:
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()
            Frame = run(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()
