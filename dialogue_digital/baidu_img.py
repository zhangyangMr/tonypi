import time

import requests
import json
from urllib.parse import urlencode, quote, quote_plus
import base64
from PIL import Image
import io
import logging

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')

API_KEY = "IcpHJQD8UDlGSJYSV1mGNlyP"
SECRET_KEY = "dmiYdzdmEBecaFqiWnquPAXSPqlEqCCF"


def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = quote_plus(content)
    return content


def result(task_id: str):
    url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/image-understanding/get-result?access_token=" + get_access_token()

    data = {
        "task_id": task_id,
    }

    payload = json.dumps(data, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json'
    }

    while True:
        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
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


def request(question: str):
    url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/image-understanding/request?access_token=" + get_access_token()

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

    if response.status_code == 200:
        responseJson = response.json()
        logging.info(f"request response {responseJson}")
        return responseJson["result"]["task_id"]
    else:
        return None


if __name__ == '__main__':
    question = "说说你都看到了什么?"
    task_id = request(question)
    time.sleep(5)
    if task_id is not None:
        desc = result(task_id)
        if desc is not None:
            logging.info(desc)
        else:
            logging.info("无法识别")
    else:
        logging.info("百度AI识别故障")
