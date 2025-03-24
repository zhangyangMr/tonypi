# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Model(ABC):
    """
    工厂模式

    chat: 和大模型交互
    """

    @abstractmethod
    def chat(self, prompt, **kwargs):
        pass
