# -*- coding: utf-8 -*-
from robot.llm.baidu_qianfan_model import BaiDuQianFanModel
from robot.llm.ali_tongyi_qianwen_model import AliTongYiQianWenModel
from robot.llm.bobfintech import BobfintechModel


class ModelFactory:
    @staticmethod
    def get_model(model_type, api_url, api_key, secret_key=None):
        """
        根据model_type获取对应大模型实例

        param:
        model_type (str): 大模型类型(bobfintech、baidu、ali)。
        api_url (str): 大模型路径地址。
        api_key (str): 大模型api_key。
        secret_key (str): secret_key。

        return:
        Model : 返回工厂对象。
        """
        if model_type == "bobfintech":
            return BobfintechModel(api_url, api_key)
        elif model_type == "baidu":
            return BaiDuQianFanModel(api_url)
        elif model_type == "ali":
            return AliTongYiQianWenModel(api_url)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
