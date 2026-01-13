#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024-04-28 14:12
# @Author  : Jack
# @File    : PyWeb

"""
PyWeb
"""

import socket
import urllib.request
import logging

import requests

from NStudyPy import PyFile


def get_host_ip() -> str:
    """
        Returns the host ip.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('114.114.114.114', 80))
    return s.getsockname()[0]


def save_file_from_url(url: str, file_path: str = None, header: dict = None) -> bool:
    """
    从合法的URL保存文件
    :param url: 合法的URL
    :param file_path: 绝对路径或相对路径, 默认使用url中的文件名
    :param header:
    :return: bool
    """
    try:
        if file_path is None or len(file_path) == 0:
            file_path = get_filename_from_url(url)
        else:
            PyFile.makedirs(file_path, is_file=True)
        req = urllib.request.Request(url)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0')
        req.add_header('Host', urllib.parse.urlparse(url).hostname)
        if header:
            for key, value in header.items():
                if value is None:
                    continue
                req.add_header(key, value)
        with urllib.request.urlopen(req) as res:
            data = res.read()
            with open(file_path, 'wb') as f:
                f.write(data)
    except Exception as e:
        logging.error(f'save_file_from_url error: {e}')
        return False
    return True


def get_filename_from_url(url: str) -> str:
    """
    从合法的URL获取文件名
    :param url: 合法的URL
    :return: str 文件名
    """
    return urllib.parse.urlparse(url).path.split('/')[-1]


def get(url, params=None, **kwargs) -> requests.Response:
    """
    GET 请求

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return request("get", url, params=params, **kwargs)


def post(url, data=None, json=None, **kwargs) -> requests.Response:
    """
    POST 请求

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    return request("post", url, data=data, json=json, **kwargs)


def request(method, url, **kwargs) -> requests.Response:
    """
    通用请求

    :param method: method for the new :class:`Request` object: ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
    :param url: URL for the new :class:`Request` object.
    :param kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    res = requests.request(method, url, **kwargs)
    res.encoding = 'utf-8'
    return res
