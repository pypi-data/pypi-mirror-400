"""词汇审查插件配置模块。

定义了插件所需的配置项，通过 NoneBot 的全局配置加载。
"""

from pathlib import Path

from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """插件配置模型。

    Attributes:
        send_word_priority: 插件的事件响应优先级。
    """

    send_word_priority: int = 100


# 加载插件配置
plugin_config = get_plugin_config(Config)