# -*- coding: utf-8 -*-
"""
    utils.tool
    ~~~~~~~~~~

    Common function.

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

import requests
from re import compile, split
from datetime import datetime, timedelta
from flask import Response, jsonify
from sys import version_info
from posixpath import join as posixjoin
from typing import List, Dict, Union
from .log import Logger

ip_pat = compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
comma_Pat = compile(r"\s*,\s*")

logger = Logger("sys").getLogger

#: 对外接口返回类型
ApiResType = Dict[str, Union[str, List, Dict]]

#: 错误字段名称
E: str = "errors"


def new_res() -> ApiResType:
    """生成面向API的响应数据结构
    - errors str: 如果出错，此字段有效，且包含具体信息
    """
    return dict()


def timeChange(timestring: str) -> str:
    """将形如2017-01-19T02:05:58.129161072Z的UTC转化为本地时间字符串"""
    startedat = timestring.replace("T", " ")[:19]
    try:
        dt = datetime.strptime(startedat, "%Y-%m-%d %H:%M:%S") + timedelta(
            hours=8
        )
        res = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.warn(e, exc_info=True)
    else:
        return res


def ip_check(ip: str) -> bool:
    return ip and isinstance(ip, str) and ip_pat.match(ip)


def string2dict(string):
    """把规律性字符串转化为字典"""
    if string:
        data = {}
        for _ in split(comma_Pat, string):
            k, v = _.split("=")
            data.update({k: v})
    else:
        data = {}
    return data


def raise_version():
    vs = version_info
    if (vs[0], vs[1]) < (3, 6):
        raise RuntimeError("The system requires version 3.6+")


class JsonResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(JsonResponse, cls).force_type(rv, environ)


def try_request(
    url,
    params=None,
    data=None,
    headers=None,
    timeout=5,
    method="post",
    verify=True,
    num_retries=1,
) -> requests.Response:
    """
    :param dict params: 请求查询参数
    :param dict data: 提交表单数据
    :param dict headers: 请求头
    :param int timeout: 超时时间，单位秒
    :param str method: 请求方法，get、post、put、delete
    :param bool verify: 验证SSL
    :param int num_retries: 超时重试次数
    """
    method = method.lower()
    if method == "get":
        method_func = requests.get
    elif method == "post":
        method_func = requests.post
    elif method == "put":
        method_func = requests.put
    elif method == "delete":
        method_func = requests.delete
    elif method == "head":
        method_func = requests.head
    else:
        method_func = requests.post
    try:
        resp = method_func(
            url,
            params=params,
            headers=headers,
            data=data,
            timeout=timeout,
            verify=verify,
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        if num_retries > 0:
            return try_request(
                url,
                params=params,
                data=data,
                headers=headers,
                timeout=timeout,
                method=method,
                verify=verify,
                num_retries=num_retries - 1,
            )
        else:
            raise
    except (requests.exceptions.RequestException, Exception):
        raise
    else:
        return resp


def uri_path_join(*paths: str) -> str:
    return posixjoin("/", *paths).rstrip("/")
