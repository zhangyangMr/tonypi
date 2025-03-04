# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Union, Any
import requests
import logging

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')


class MaaSApiChain(object):

    def __init__(self, api_url: str, api_key: str):
        """
        :param cfg:
        """
        self.api_url = api_url
        self.api_key = api_key

    def chat(self, query: str, streaming: bool = False, conversation_id: str = None) -> Any:
        """
        与模型进行交互
        :param conversation_id:
        :param query:
        :param streaming:
        :return:
        """
        logging.info(f"api url: {self.api_url}; api key: {self.api_key}")

        headers = {
            'MAAS-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'inputs': {},
            'query': query,
            'streaming': streaming,
            'with_history': False
        }
        if conversation_id is not None:
            data['conversationId'] = conversation_id

        logging.info(f"request data: {data}")

        response = requests.post(self.api_url, headers=headers, json=data)

        return response
