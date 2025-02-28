import json
import time
import logging
import threading
import wave
import pyaudio
import base64
from websocket import create_connection
from queue import Queue

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')


class TTSClient:
    def __init__(self, uri):
        self.uri = "wss://{}".format(uri)
        self.ssl_context = None
        self.ssl_opt = None
        self.websocket = None
        self.running = False
        self.msg_queue = Queue()

    def connect(self):
        """建立 WebSocket 连接"""
        try:
            self.websocket = create_connection(self.uri, ssl=self.ssl_context, sslopt=self.ssl_opt)
            logging.info(f"Connected to WebSocket server at {self.uri}")
        except Exception as e:
            logging.error(f"Failed to connect to WebSocket server: {e}")
            raise

    def send_message(self, message: str, wait_time=5):
        """发送消息到 WebSocket 服务器"""
        if self.websocket:
            tmp_msg = json.dumps(
                {
                    "text": message,
                    "speed": 1.0,
                    "role": "byjk_female_康玥莹01",
                    "sample_rate": 15000,
                    "chunk_size": 12000,
                })
            self.websocket.send(tmp_msg)
            logging.info(f"Sent message: {tmp_msg}")

    def receive_message(self):
        """接收来自 WebSocket 服务器的消息"""
        logging.info("start Receive message")
        CHUNK = 1024  # 每个缓冲区的帧数
        FORMAT = pyaudio.paInt16  # 音频格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 采样率
        p = pyaudio.PyAudio()
        # 打开扬声器输出流
        output_stream = p.open(format=FORMAT,
                               channels=CHANNELS,
                               rate=RATE,
                               output=True,
                               frames_per_buffer=CHUNK)

        while self.running:
            try:
                message = self.websocket.recv()
                data = json.loads(message)
                # logging.info(f"Received message: {data['speech']}")
                if data['speech'] is None:
                    logging.info("声音接收成功")
                else:
                    # logging.info("播放声音")
                    audio_data = base64.b64decode(data['speech'])
                    output_stream.write(audio_data)
            except Exception as e:
                logging.error(f"Error receiving message: {e}")
                break

    def close(self):
        """关闭 WebSocket 连接"""
        if self.websocket:
            self.websocket.close()
            logging.info("WebSocket connection closed")

    def start(self):
        """启动发送和接收线程"""
        self.running = True
        self.connect()

        # 创建发送线程
        # self.send_thread = threading.Thread(target=self.send_messages)
        # self.send_thread.start()

        # 创建接收线程
        self.recv_thread = threading.Thread(target=self.receive_message)
        self.recv_thread.start()

    def stop(self):
        """停止线程并关闭连接"""
        self.running = False
        # self.send_thread.join()
        self.recv_thread.join()
        self.close()

    def send_messages(self):
        """循环发送消息"""
        messages = [
            json.dumps(
                {
                    "text": "秋日的阳光洒满大地，金黄的树叶在微风中轻轻摇曳。漫步在林间小道上，脚下是松软的落叶，耳边是鸟儿的清脆鸣叫。空气中弥漫着泥土的芬芳，仿佛大自然在低声诉说着季节的更替。这一刻，时间仿佛静止，心灵也随着宁静的景色沉静下来。秋天，不仅是收获的季节，更是感受生命美好的时刻。",
                    "speed": 1.0,
                    "role": "byjk_female_康玥莹01",
                    "sample_rate": 15000,
                    "chunk_size": 12000,
                }),
        ]

        for msg in messages:
            logging.info(msg)
            self.send_message(msg)
            time.sleep(2)  # 每隔 2 秒发送一条消息


# if __name__ == "__main__":
#     # WebSocket 服务器地址
#     ws_uri = "chats-ai-bobfin-prep.tests.net.cn/innovationteam/multimodal/voice/tts/stream"
#
#     # 创建 WebSocket 客户端实例
#     client = TTSClient(ws_uri)
#
#     try:
#         # 启动 WebSocket 客户端
#         client.start()
#         client.send_message(".")
#         client.send_message("启动中")
#         client.send_message("启动中")
#         # client.send_messages()
#         # client.send_message(tmp_data)
#         # 主线程等待一段时间后停止
#         time.sleep(600)
#     finally:
#         # 停止 WebSocket 客户端
#         client.stop()
#
#     logging.info("Program finished.")
