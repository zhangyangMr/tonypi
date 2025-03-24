# -*- coding: utf-8 -*-
from robot.llm.llm_model import Model
import logging
import requests


class BobfintechModel(Model):
    """对接北银金科MaaS平台"""

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def chat(self, prompt, **kwargs):
        """
        实现北银金科MaaS平台的调用逻辑

        param:
        prompt (str): 问题内容。
        streaming (bool): 是否开启流式输出。
        conversation_id (str): 关联上下文ID。

        return:
        response (dict): 返回答案对象。
        """

        logging.info(f"Calling BobfintechModel with prompt: {prompt}")

        streaming = kwargs.get('streaming', False)
        conversation_id = kwargs.get('conversation_id', None)

        headers = {
            'MAAS-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'inputs': {},
            'query': prompt,
            'streaming': streaming,
            'with_history': False
        }
        if conversation_id is not None:
            data['conversationId'] = conversation_id

        logging.info(f"request data: {data}")

        response = requests.post(self.api_url, headers=headers, json=data)

        return response
