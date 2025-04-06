# tonypi相关代码

## 1. 代码目录结构

```shell
.
├── camera                  # 调用摄像头进行图像内容识别代码
├── dialogue_digital        # 对接公司maas和语音服务，实现机器人语音对话和指令执行代码
├── prompt                  # 相关提示词
├── README.md               # 说明文档
├── TonyPi                  # 幻尔机器人内部相关代码（示例代码和hiwonder-sdk）
├── face_check_in           # 人脸签到单独功能代码
├── face_recognition        # 人脸识别单独功能代码
├── robot                   # 机器人集成全部功能代码

```

## 2. camera介绍

本代码通过机器人摄像头识别当前镜头内存在的物品，通过调用百度AI图像理解功能实现。

### 2.1 配置文件llm_conf.yaml

```yaml
maas_api_conf:
  maas_api_url: ''   # 配置maas地址
  maas_api_key:      
    common_use: ''   # 配置maaskey
  asr_url: ''        # 配置asr地址
  tts_url: ''        # 配置tts地址
sys_conf:
  cfg_path: ''
  write_file_dir: ''
```

### 2.2 baidu_img.py

以下key可以从https://ai.baidu.com/tech/imagerecognition/image_understanding 申请试用

```py
API_KEY = ""   # 从百度AI开放平台申请，图像内容理解功能
SECRET_KEY = ""  # 从百度AI开放平台申请，图像内容理解功能
```

## 3. promt介绍

maas创建应用相关提示词

## 4. TonyPi 介绍

幻尔机器人内部相关代码（示例代码和hiwonder-sdk）

```shell
.
├── ActionGroupDict.py
├── Camera.py
├── Command.txt
├── Example
├── Extend
├── Functions                       # 幻尔机器人自带示例
├── HiwonderSDK                     # 操作幻尔机器人 SDK
├── Joystick.py
├── KickBall_only_once.py
├── KickBall_only.py
├── lab_config.yaml
├── little_apple.py
├── MjpgServer.py
├── OpenVINO
├── RPCServer.py
├── servo_config.yaml
├── TonyPi.py
├── Transport_only.py
└── yaml_handle.py
```

