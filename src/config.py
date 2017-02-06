# -*- coding:utf8 -*-
#
# Breezes配置文件, 默认先读取环境变量, 格式: os.getenv("环境变量", "默认值")
#

import os

#全局配置段
GLOBAL={

    "Host": os.getenv("breezes_host", "0.0.0.0"),
    #应用监听地址

    "Port": int(os.getenv("breezes_port", 10210)),
    #应用监听端口

    "Debug": os.getenv("breezes_debug", True),
    #Debug, 开发环境是True, 生产环境是False, 这是默认配置

    "LogLevel": os.getenv("breezes_loglevel", "DEBUG"),
    #应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL
}

#生产环境配置段
PRODUCT={

    "ProcessName": "Breezes",
    #自定义进程名称

    "ProductType": os.getenv("breezes_producttype", "tornado"),
    #生产环境启动方法，可选`gevent`, `tornado`。
}
