#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025-03-18 11:15
# @Author  : Jack
# @File    : PyLogger

"""
PyLogger
"""
import logging
from logging.handlers import TimedRotatingFileHandler
import os


def get_logger(name=None, logs_dir='logs'):
    """
    获取一个配置好的 logger 实例。
    :param name: logger 名称
    :param logs_dir: 日志文件存放目录
    :return:
    """
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(threadName)s %(levelname)s：%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(),
                TimedRotatingFileHandler(f'{logs_dir}/app.log', when="midnight", interval=1, backupCount=365, encoding='utf-8')
            ],
        )
    return logging.getLogger(name)


if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Logger is working.")
