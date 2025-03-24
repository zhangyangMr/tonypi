# -*- coding: utf-8 -*-
import logging
import base64
import re
from urllib.parse import urlencode, quote, quote_plus
from pypinyin import pinyin, lazy_pinyin, Style  # 需要安装 pypinyin 模块


def deal_maas_response(response):
    """
    对MaaS大模型返回结果进行统一数据处理

    param:
    response : MaaS大模型返回的响应。

    return:
    data : 返回response中解析的data数据。
    """
    if response.status_code == 200:
        chat_result = response.json()
        if chat_result.get("code") == 200:
            return chat_result.get("data")
        else:
            logging.error(f"抱歉调用大模型错误，错误代码{response.status_code}")
            return None
    else:
        logging.error(f"抱歉调用大模型错误，错误代码{response.status_code}")
        return None


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


def starts_with_chinese_pinyin(sentence, chinese_word):
    """
    判断字符串是否以某个中文词的发音开头

    :param text: 待检查的字符串
    :param chinese_word: 中文词

    :return: 如果以该中文词的发音开头，返回 True，否则返回 False
    """

    # 判断句子长度是否大于等于4
    if len(sentence) < 4:
        return False

    # text = sentence[:4]
    text = sentence

    # 将中文词转换为拼音
    word_pinyin = lazy_pinyin(chinese_word)
    text_pinyin = lazy_pinyin(text)

    logging.info(f"word_pinyin: {word_pinyin}")
    logging.info(f"text_pinyin: {text_pinyin}")

    word_pinyin_str = ''.join(word_pinyin)
    text_pinyin_str = ''.join(text_pinyin)

    return contains_substring(text_pinyin_str.lower(), word_pinyin_str.lower())


def contains_substring(text, substring):
    """
    判断字符串是否包含某个子字符串

    :param text: 待检查的字符串
    :param substring: 需要匹配的子字符串

    :return: 如果包含子字符串，返回 True，否则返回 False
    """
    escaped_substring = re.escape(substring)
    if re.search(escaped_substring, text):
        return True
    else:
        return False
