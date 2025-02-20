# -*- coding: utf-8 -*-
import os.path

import yaml
import json
from typing import Any


def reflect_json_2_class(json_value, data_class):
    return data_class(**json_value)


# 读取配置文件
def read_llm_cfg(cfg_path) -> Any:
    with open(cfg_path, 'r', encoding='utf-8') as read_handler:
        contents = read_handler.read()
    llm_cfg = yaml.load(contents, yaml.FullLoader)
    return llm_cfg


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as read_handler:
        contents = read_handler.read()

    file_name = os.path.basename(file_path)
    return contents, file_name


def write_file(file_path, contents):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(contents)


def write_stream_data_2_file(file_path, stream_data):
    with open(file_path, 'w', encoding='utf-8') as file:
        for chunk in stream_data.iter_lines(chunk_size=1024, decode_unicode=True):
            if chunk:
                data = json.loads(chunk[6:])
                file.write(data['content'])
