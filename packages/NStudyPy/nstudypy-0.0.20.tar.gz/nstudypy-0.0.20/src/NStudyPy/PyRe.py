#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-07-10 15:27
# @Author  : Jack
# @File    : PyRe

"""
PyRe
"""
import re

# 身份证号
_id_card = re.compile(r'(^\d{15}$)|(^\d{17}[\dXx]$)')


def format_id_card(id_card_string):
    """
    格式化身份证号码
    :param id_card_string:
    :return:
    """
    match = _id_card.search(id_card_string)
    if match:
        old_id_card, id_card = match.groups()
        return id_card or old_id_card
    else:
        return ""
