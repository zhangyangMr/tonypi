import time

import requests
import json
import logging
from robot.config.config import load_config
from robot.utils.utils import get_file_content_as_base64


class BaiduImgs:
    """调用百度图片内容理解接口"""

    def __init__(self, token_url, api_url, API_KEY, SECRET_KEY):
        """
        使用 AK，SK 生成鉴权签名（Access Token）

        :param token_url: 获取百度图片内容理解token地址
        :param api_url: 百度图片内容理解地址
        :param API_KEY: 访问百度图片内容理解的API_KEY
        :param SECRET_KEY: SECRET_KEY
        """
        self.token_url = token_url
        self.api_url = api_url
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY

        params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
        self.access_token = str(requests.post(token_url, params=params).json().get("access_token"))

    def request(self, question: str):
        """
        请求百度图片理解接口，进行图片内容理解人物处理请求

        :param question: 对需要识别的图片，提问的问题

        :return task_id: 返回处理的任务ID
        """
        url = self.api_url + "/request?access_token=" + self.access_token

        img_path = "./frame.jpg"

        content = get_file_content_as_base64(img_path, urlencoded=False)

        data = {
            "image": content,
            "question": question
        }

        payload = json.dumps(data, ensure_ascii=False)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        logging.info(f"response{response}")

        if response.status_code == 200:
            responseJson = response.json()
            logging.info(f"request response {responseJson}")
            return responseJson["result"]["task_id"]
        else:
            return None

    def result(self, task_id: str):
        """
        请求百度图片理解接口，进行图片内容理解人物处理结果获取

        :param task_id: 获取处理结果的任务ID

        :return description: 返回理解的图片内容
        """

        url = self.api_url + "/get-result?access_token=" + self.access_token

        data = {
            "task_id": task_id,
        }

        payload = json.dumps(data, ensure_ascii=False)
        headers = {
            'Content-Type': 'application/json'
        }

        while True:
            response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
            logging.info(f"result response{response}")
            if response.status_code == 200:
                responseJson = response.json()
                logging.info(f"request response {responseJson}")
                result_info = responseJson.get("result")
                if result_info["ret_msg"] == "processing":
                    time.sleep(2)
                    continue
                elif result_info["ret_msg"] == "success":
                    return responseJson["result"]["description"]
                else:
                    return None
            else:
                return None


if __name__ == '__main__':
    # 加载配置文件
    config_path = '../config/config.yaml'
    config = load_config(config_path)

    # 配置日志级别
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

    token_url = config.get("img_understand")["baidu_conf"]["token_url"]
    api_url = config.get("img_understand")["baidu_conf"]["api_url"]
    api_key = config.get("img_understand")["baidu_conf"]["api_key"]
    secret_key = config.get("img_understand")["baidu_conf"]["secret_key"]
    baidu_img = BaiduImgs(token_url=token_url, api_url=api_url, API_KEY=api_key, SECRET_KEY=secret_key)

    question = "说说你都看到了什么?"

    task_id = baidu_img.request(question)
    time.sleep(5)

    if task_id is not None:
        desc = baidu_img.result(task_id)
        if desc is not None:
            logging.info(desc)
        else:
            logging.info("无法识别")
    else:
        logging.info("百度AI识别故障")
