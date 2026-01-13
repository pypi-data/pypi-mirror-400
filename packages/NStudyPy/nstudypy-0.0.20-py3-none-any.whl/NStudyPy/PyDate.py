#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-04-26 10:00
# @Author  : Jack
# @File    : PyDate

"""
PyDate
"""
import re
from datetime import datetime

DATE_FORMAT_YYYYMMDD = '%Y%m%d'
DATE_FORMAT_YYYY_MM_DD = '%Y-%m-%d'
DATE_FORMAT_YYYYMMDD_EX = '%Y%m%d%H%M%S'

_reg_date = re.compile(r'(\d{2,4}).*?(\d{1,2}).*?(\d{1,2})')


def get_date(date: datetime = None, date_format: str = DATE_FORMAT_YYYYMMDD) -> str:
    """
    获取当前日期特定格式
    :param date: 日期
    :param date_format:
        %Y：四位数的年份（例如：2024）
        %m：月份（01 到 12）
        %d：日期（01 到 31）
        %H：小时（24 小时制，00 到 23）
        %I：小时（12 小时制，01 到 12）
        %M：分钟（00 到 59）
        %S：秒（00 到 59）
        %a：星期几的缩写名称（例如：Mon）
        %A：星期几的完整名称（例如：Monday）
        %b：月份的缩写名称（例如：Jan）
        %B：月份的完整名称（例如：January）
        %c：本地日期时间表示（例如：Tue Apr 30 14:21:08 2024）
        %x：本地日期表示（例如：04/30/24）
        %X：本地时间表示（例如：14:21:08）
        除了上述常用的格式指令之外，还可以使用以下指令来表示不同的日期和时间组件：

        %j：一年中的第几天（001 到 366）
        %U：一年中的第几周（以周日作为一周的开始，00 到 53）
        %W：一年中的第几周（以周一作为一周的开始，00 到 53）
        %w：星期几（0 是周日，6 是周六）
        %Z：时区名称（例如：EST）
    :return:
    """
    if date is None:
        date = get_now()
    return date.strftime(date_format)


def to_date(date_string: str, date_format: str = DATE_FORMAT_YYYY_MM_DD) -> datetime:
    """
    字符串转日期
    :param date_string:
    :param date_format: 见 get_date date_format
    :return:
    """
    return datetime.strptime(date_string, date_format)


def get_now() -> datetime:
    """
    获取当前时间
    :return:
    """
    return datetime.now()


def format_date(date_str: str) -> str:
    """
    格式化日期字符串
    :param date_str: 任意包含日期的字符串
    :return: 格式化后的日期字符串 yyyy-mm-dd日
    """
    match = _reg_date.search(date_str)
    if match:
        year, month, day = match.groups()
        if len(year) == 2:
            year = '20' + year
        elif len(year) == 3:
            year = '2' + year
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    else:
        return None
