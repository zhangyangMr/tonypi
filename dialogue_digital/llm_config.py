from dataclasses import dataclass
from typing import List


@dataclass
class MaasApiKey:
    robot: str  # 机器人指令大模型key
    chat: str  # 机器人文档大模型key
    classify: str  # 机器人问题分类大模型key


@dataclass
class MaasApiConf:
    maas_api_url: str
    maas_api_key: MaasApiKey
    asr_url: str
    tts_url: str
    tts_base_url: str


@dataclass
class SysConf:
    cfg_path: str
    write_file_dir: str


@dataclass
class LLMConfig:
    maas_api_conf: MaasApiConf
    sys_conf: SysConf
