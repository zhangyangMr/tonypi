# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Union, Any
import requests
import logging
from urllib.parse import urlencode
from utils_sound import play_mp3_file
from pyttsx3_tts import play_sound


class TTSApiChain(object):

    def __init__(self, host: str):
        """
        :param host: tts服务的地址
        """
        self.host = host

    def postTTS(self, url: str, params: dict) -> Any:
        """
        与模型进行交互
        :param url: 请求路径url
        :param params: 请求参数

        :return: 返回tts响应信息
        """

        headers = {
            'Content-Type': 'application/json'
        }

        data = params

        url = self.host + url

        response = requests.post(url, headers=headers, data=json.dumps(data))

        return response

    def getTTS(self, url: str, params: Any | None = None) -> Any:
        """
        与模型进行交互
        :param url: 请求路径url
        :param params: 请求参数

        :return: 返回tts响应信息
        """

        url = self.host + url

        logging.info(f"url:{url}")

        response = requests.get(url, data=params)

        return response


def text_to_wav_file(text, host):
    """
    请求tts服务，将文字转为语音进行播放
    :param text: 需要合成语音的文字
    :param host: tts服务的请求地址
    """
    play_sound(text)
    return

    """将text文本转为wav音频文件"""
    tts_client = TTSApiChain(host)

    url = "/multimodal/voice/tts/file"

    data = {
        "text": text,
        "speed": 1.0,
        "role": "byjk_male_男播音4号",
        "sample_rate": 16000,
    }
    logging.info(f"text_to_wav_file data:{data}")
    encoded_data = urlencode(data)

    query_url = f"{url}?{encoded_data}"
    logging.info(f"query_url :{query_url}")

    response = tts_client.getTTS(query_url)
    if response.status_code == 200:
        play_mp3_file(response.content)
    else:
        logging.info(f"请求失败，状态码：{response.status_code}")


if __name__ == "__main__":
    text_to_wav_file("你好，小爱同学", "")
