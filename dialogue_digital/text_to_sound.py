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

    def send_message(self, message, wait_time=5):
        """发送消息到 WebSocket 服务器"""
        # CHUNK = 1024  # 每个缓冲区的帧数
        # FORMAT = pyaudio.paInt16  # 音频格式
        # CHANNELS = 1  # 单声道
        # RATE = 16000  # 采样率
        # p = pyaudio.PyAudio()
        # # 打开扬声器输出流
        # output_stream = p.open(format=FORMAT,
        #                        channels=CHANNELS,
        #                        rate=RATE,
        #                        output=True,
        #                        frames_per_buffer=CHUNK)
        if self.websocket:
            self.websocket.send(message)
            logging.info(f"Sent message: {message}")
            # while True:
            #     msg = self.msg_queue.get(timeout=wait_time)
            #     logging.info(f"Sent message get : {msg}")
            #     if self.msg_queue.empty():
            #         break
            #     logging.info(f"Sent message get : {msg}")
            #     audio_data = base64.b64decode(msg)
            #     output_stream.write(audio_data)

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
                    # self.msg_queue.put(data['speech'])
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
                {"text": "1111哪吒2你看了吗，请说一下哪吒2为什么爆火？", "speed": 1.0, "role": "byjk_female_康玥莹01",
                 "sample_rate": 16000}),
        ]

        for msg in messages:
            self.send_message(msg)
            time.sleep(2)  # 每隔 2 秒发送一条消息


# if __name__ == "__main__":
#     # WebSocket 服务器地址
#     ws_uri = "chats-ai-bobfin-prep.tests.net.cn/innovationteam/multimodal/voice/tts/stream"
#
#     # 创建 WebSocket 客户端实例
#     client = WebSocketClient(ws_uri)
#
#     try:
#         # 启动 WebSocket 客户端
#         client.start()
#         client.send_messages()
#         # 主线程等待一段时间后停止
#         time.sleep(600)
#     finally:
#         # 停止 WebSocket 客户端
#         client.stop()
#
#     logging.info("Program finished.")
