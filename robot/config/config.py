# -*- coding: utf-8 -*-
import yaml
import os
import logging


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


if __name__ == "__main__":
    # 示例：加载配置文件
    config_path = './config.yaml'
    config = load_config(config_path)

    # 配置日志级别
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')
    logging.info(f"Loaded config: {config}")
