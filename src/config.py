# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

from os import getenv

GLOBAL = {
    "ProcessName": "Breezes",
    # 自定义进程名称
    "Host": getenv("breezes_host", "0.0.0.0"),
    # 应用监听地址
    "Port": int(getenv("breezes_port", 10210)),
    # 应用监听端口
    "LogLevel": getenv("breezes_loglevel", "DEBUG"),
    # 应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL
}

SITE = {
    "URIPrefix": getenv("breezes_uri_prefix", "/"),
    # URL路由前缀
    "ICP": getenv("breezes_icp"),
    # 备案号
    "PersistentDirectory": getenv("breezes_persistent_dir"),
    # 持久化数据存放目录，默认放在当前 `.db` 目录下
}
