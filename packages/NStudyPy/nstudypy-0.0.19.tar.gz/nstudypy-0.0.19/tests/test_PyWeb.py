#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-06-06 14:50
# @Author  : Jack
# @File    : test_PyWeb

"""
test_PyWeb
"""

from NStudyPy import PyWeb

if __name__ == '__main__':
    # url = 'https://www.baidu.com/img/pc/result.png?x=1&2=1'
    # print(PyWeb.get_filename_from_url(url))

    res = PyWeb.get('https://baidu.com')
    print(res.text)
