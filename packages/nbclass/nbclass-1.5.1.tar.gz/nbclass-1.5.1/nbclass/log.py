# -*- coding: utf-8 -*-
"""
@ Created on 2024-09-04 15:37
---------
@summary:
---------
@author: XiaoBai
"""
import os
import sys
import logging
from pprint import pformat

from loguru import logger

# 获取根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录添加到path中
sys.path.append(BASE_DIR)


class InterceptHandler(logging.Handler):

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    format_string = '<level>{level: <8}</level>' \
                    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - ' \
                    '<cyan>{name}</cyan>.<cyan>{function}</cyan>:' \
                    '<cyan>{line}</cyan> - ' \
                    '<level>{message}</level>'

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"

    return format_string
