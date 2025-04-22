# -*- coding: utf-8 -*-
import logging
from face import *
from utils import load_config
from camera import call_camera

if __name__ == '__main__':
    # 加载配置文件
    config_path = './config.yaml'
    config = load_config(config_path)

    tts_url = config.get('tts')['base_url']

    # 配置日志级别
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')
    logging.info(f"Loaded config: {config}")

    logging.info("face sign in start")
    call_camera(tts_url,config)
