import ssl
import wave
from websocket import ABNF
from websocket import create_connection
from queue import Queue
import threading
import traceback
import json
import time
import numpy as np
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s")


class AsrOnline:
    def __init__(self, uri, is_ssl, chunk_size, mode, chunk_interval=10, wav_name="default"):
        try:
            if is_ssl == True:
                ssl_context = ssl.SSLContext()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                uri = "wss://{}".format(uri)
                ssl_opt = {"cert_reqs": ssl.CERT_NONE}
            else:
                uri = "wss://{}".format(uri)
                ssl_context = None
                ssl_opt = None

            self.msg_queue = Queue()  # used for recognized result text

            logging.info(f"connect to url {uri}")
            self.websocket = create_connection(uri, ssl=ssl_context, sslopt=ssl_opt)

            self.thread_msg = threading.Thread(target=AsrOnline.thread_rec_msg, args=(self,))
            self.thread_msg.start()

            chunk_size = [int(x) for x in chunk_size.split(",")]
            message = json.dumps(
                {"mode": mode, "chunk_size": chunk_size, "encoder_chunk_look_back": 4, "decoder_chunk_look_back": 1,
                 "chunk_interval": chunk_interval, "wav_name": wav_name, "is_speaking": True})

            self.websocket.send(message)

            logging.info(f"send json {message}")

        except Exception as e:
            logging.error(f"Exception:{e}")
            traceback.print_exc()

    # threads for rev msg
    def thread_rec_msg(self):
        try:
            while True:
                msg = self.websocket.recv()
                if msg is None or len(msg) == 0:
                    continue
                msg = json.loads(msg)

                self.msg_queue.put(msg)
        except Exception as e:
            logging.info("client closed")

    # feed data to asr engine, wait_time means waiting for result until time out
    def feed_chunk(self, chunk, wait_time=0.01):
        try:
            self.websocket.send(chunk, ABNF.OPCODE_BINARY)
            # loop to check if there is a message, timeout in 0.01s
            while True:
                msg = self.msg_queue.get(timeout=wait_time)
                if self.msg_queue.empty():
                    break
            return msg
        except:
            return ""

    def close(self, timeout=1):
        message = json.dumps({"is_speaking": False})
        self.websocket.send(message)
        # sleep for timeout seconds to wait for result
        time.sleep(timeout)
        msg = ""
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()

        self.websocket.close()
        # only resturn the last msg
        return msg

# if __name__ == '__main__':
#     print('INFO - example for Funasr_websocket_recognizer')
#
#     # wav_path = "audio0.wav"
#     wav_path = "audio0.wav"
#
#     with wave.open(wav_path, "rb") as wav_file:
#         params = wav_file.getparams()
#         frames = wav_file.readframes(wav_file.getnframes())
#         audio_bytes = bytes(frames)
#
#     stride = int(60 * 10 / 10 / 1000 * 16000 * 2)
#     chunk_num = (len(audio_bytes) - 1) // stride + 1
#
#     # create an recognizer
#     # rcg = Funasr_websocket_recognizer(uri="172.16.7.103:10086", is_ssl=False, chunk_size="0,10,5", mode="2pass")
#     # rcg = Funasr_websocket_recognizer(uri="ai.bobfintech.com.cn/webaiasr-api/", is_ssl=False, chunk_size="-1, 10, 5", mode="2pass")
#     rcg = AsrOnline(
#         uri="chats-ai-bobfin-prep.tests.net.cn/innovationteam/multimodal/voice/asr/asr_online", is_ssl=False,
#         chunk_size="-1, 10, 5", mode="2pass")
#     # rcg = Funasr_websocket_recognizer(uri="chats-ai-bobfin-prep.tests.net.cn", is_ssl=False, chunk_size="-1, 10, 5", mode="2pass")
#
#     # loop to send chunk
#     for i in range(chunk_num):
#         beg = i * stride
#         data = audio_bytes[beg:beg + stride]
#
#         text = rcg.feed_chunk(data, wait_time=0.02)
#         if len(text) > 0:
#             print("text", text)
#         time.sleep(0.05)
#
#     # get last message
#     text = rcg.close(timeout=1)
#     print("text", text)