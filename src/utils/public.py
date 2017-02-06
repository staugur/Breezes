# -*- coding: utf8 -*-

import re
import uuid
import datetime
import hashlib
from .syslog import Syslog

md5             = lambda pwd:hashlib.md5(pwd).hexdigest()
ip_pat          = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
comma_Pat       = re.compile(r"\s*,\s*")
logger          = Syslog.getLogger()
gen_requestId   = lambda :str(uuid.uuid4())

def timeChange(timestring):
    """ 将形如2017-01-19T02:05:58.129161072Z转化为可读性高的字符串 """

    logger.debug("Change time, source time is %s" %timestring)
    startedat = timestring.replace('T', ' ')[:19]
    try:
        dt  = datetime.datetime.strptime(startedat, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)
        res = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception, e:
        logger.warn(e, exc_info=True)
    else:
        logger.debug("Change time, result time is %s" %res)
        return res

def ip_check(ip):
    logger.info("the function ip_check param is %s" %ip)
    if isinstance(ip, (str, unicode)):
        return ip_pat.match(ip)

def string2dict(string):
    """ 把规律性字符串转化为字典 """
    if string:
        data = {}
        for _ in re.split(comma_Pat, string):
            k, v = _.split("=")
            data.update({k:v})
    else:
        data = {}
    logger.info("change string2dict, return {}".format(data))
    return data
