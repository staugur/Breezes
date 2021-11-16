# -*- coding: utf-8 -*-
"""
    utils.exceptions
    ~~~~~~~~~~~~~~~~

    Error Class.

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""


class BreezesError(Exception):
    pass


class ApiError(BreezesError):
    """触发Api异常，直接中止后续执行并返回JSON格式错误"""

    def __init__(self, message, status_code=200):
        super(ApiError, self).__init__()
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = dict(errors=self.message)
        return rv
