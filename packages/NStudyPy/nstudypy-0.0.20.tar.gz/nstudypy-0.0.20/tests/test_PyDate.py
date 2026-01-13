#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-07-01 17:34
# @Author  : Jack
# @File    : test_PyDate

"""
test_PyDate
"""

from NStudyPy import PyDate

# 示例日期字符串
date_strs = [
    '有效2024-06-18', "日期:2024-06-18结束", '2024-06-18有效',
    '日期:2024/06/18', '2024/6/18', '2024年06月18日',
    '日期2024年6月8日', '24年6月8日', '024年6月8日',
]

for d in date_strs:
    print(f"原始日期字符串：{d}\t\t 格式化后字符串:\t\t{PyDate.format_date(d)}")
