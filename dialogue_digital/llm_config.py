from dataclasses import dataclass
from typing import List


@dataclass
class MaasApiKey:
    common_use: str


@dataclass
class MaasApiConf:
    maas_api_url: str
    maas_api_key: MaasApiKey
    asr_url: str
    tts_url: str


@dataclass
class SysConf:
    cfg_path: str
    write_file_dir: str


@dataclass
class LLMConfig:
    maas_api_conf: MaasApiConf
    sys_conf: SysConf
