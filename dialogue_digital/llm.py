import json

from maasapi_chain import MaaSApiChain
from llm_config import LLMConfig, MaasApiConf, MaasApiKey
from cfg_utils import reflect_json_2_class
import logging

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')


def init_maasapi_llm_chain(cfg: LLMConfig, prompt_type: str = 'common_use'):
    maas_api_cfg = reflect_json_2_class(cfg.maas_api_conf, MaasApiConf)
    llm_cfg = reflect_json_2_class(maas_api_cfg.maas_api_key, MaasApiKey)

    logging.info(f"init_maasapi_llm_chain llm_cfg: {llm_cfg}")

    api_key = ''
    api_url = maas_api_cfg.maas_api_url

    if prompt_type == 'common_use':
        api_key = llm_cfg.common_use
    else:
        api_key = llm_cfg.common_use

    chain = MaaSApiChain(api_url, api_key)

    return chain
