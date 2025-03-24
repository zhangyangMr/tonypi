# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Union, Any
import requests
import logging
from urllib.parse import urlencode
from robot.utils.utils_wav import play_mp3_from_binary, play_mp3_file


class TTSApiChain(object):

    def __init__(self, host: str):
        """
        :param cfg:
        """
        self.host = host

    def postTTS(self, url: str, params: dict) -> Any:
        """
        与模型进行交互
        :param params:
        :param url:
        :return:
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
        :param params:
        :param url:
        :return:
        """

        url = self.host + url

        logging.info(f"url:{url}")

        response = requests.get(url, data=params)

        return response


def text_to_wav_file(host, text):
    """将text文本转为wav音频文件"""
    tts_client = TTSApiChain(host)

    url = "/multimodal/voice/tts/file"

    data = {
        "text": text,
        "speed": 1.0,
        "role": "byjk_female_康玥莹01",
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
