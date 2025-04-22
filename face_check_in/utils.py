# -*- coding: utf-8 -*-
import yaml
import os
import logging
import re
from datetime import timedelta


def load_config(config_path):
    """
    从配置文件中加载配置

    param:
    config_path (str): 配置文件路径。

    return:
    config (dict): 配置文件对象。
    """

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        logging.error(f"配置文件 {config_path} 不存在")
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")

    # 读取 YAML 配置文件
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    return config


def parse_timedelta(time_str):
    """
    将时间字符串(如 1min, 30s, 2h30min)转换为 timedelta 对象
    支持的单位: h(小时), min(分钟), s(秒), ms(毫秒)

    :param time_str: 时间字符串

    :return timedelta(**parts): 时间
    """
    if not time_str:
        return timedelta()

    # 定义正则表达式匹配所有时间单位
    pattern = r'(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)min)?(?:(?P<seconds>\d+)s)?(?:(?P<milliseconds>\d+)ms)?'
    match = re.fullmatch(pattern, time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")

    parts = {k: int(v) for k, v in match.groupdict().items() if v}
    return timedelta(**parts)
