#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-06-04 15:18
# @Author  : Jack
# @File    : PyEnv

"""
PyEnv
"""

import os
import json


def update_env(config_path: str) -> None:
    """
        update home environment variables
    """
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key, value in config.items():
                os.environ[key] = value


def update_home_env(config_file: str) -> None:
    """
        update home environment variables
    """
    config_path = os.path.join(os.path.expanduser("~"), '.home', config_file)
    update_env(config_path)


def get_env(key: str, default=None, value_type=None):
    """
        Returns the value from the key.
        check environment variables
    """
    value = default

    if key in os.environ:
        value = os.environ.get(key)

    if (value_type is None) or (default is None):
        return value

    if value_type == bool:
        return value == "True"

    return value_type(value)
