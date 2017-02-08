# -*- coding: utf8 -*-

import os.path, json, requests
from utils.public import logger


class BASE_REGISTRY_API:


    def __init__(self, timeout=2, verify=False):
        self.timeout  = timeout
        self.verify   = verify

    def _checkStatus(self, url, version=1):
        """ 返回私有仓状态 """

        if url:
            url = url.strip("/") + "/v1/_ping" if version == 1 else url.strip("/") + "/v2/"
            try:
                req = requests.head(url, timeout=self.timeout, verify=self.verify)
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                logger.info(req.status_code)
                return req.ok
        return False

    def _search_all_repository(self, url, version=1, q=""):
        """ 搜索私有仓所有镜像 """

        if url:
            ReqUrl = url.strip("/") + "/v1/search" if version == 1 else url.strip("/") + "/v2/_catalog"
            logger.info("_search_all_repository for url {}".format(ReqUrl))
            try:
                Images = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify, params={"q": q}).json()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                if version == 1:
                    return Images["results"]
                else:
                    return [ {"name": _, "description": None} for _ in Images["repositories"] if q in _ ]
        return []

    def _list_image_tags(self, ImageName, url, version=1):
        """ 列出某个镜像所有标签 """

        if url:
            ReqUrl = url.strip("/") + "/v1/repositories/{}/tags".format(ImageName) if version == 1 else url.strip("/") + "/v2/{}/tags/list".format(ImageName)
            logger.info("_list_image_tag for url {}".format(ReqUrl))
            try:
                Tags = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                if version == 1:
                    return Tags
                else:
                    return { _:"digest" for _ in Tags.get('tags', []) }
        return {}

    def _delete_image(self, ImageName, url, version=1):
        """ 删除一个镜像 """

        if url:
            ReqUrl = url.strip("/") + "/v1/repositories/{}/".format(ImageName) if version == 1 else url.strip("/") + "/v2/{}/xxx".format(ImageName)
            logger.info("_delete_repository for url {}".format(ReqUrl))
            try:
                delete_repo_result = requests.delete(ReqUrl, timeout=self.timeout, verify=self.verify).json()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                return delete_repo_result
        return False

    def _image_tag(self, ImageName, tag, url, version=1):
        """ 查询某个镜像tag的imageId, 删除tag """

        if url:
            ReqUrl = url.strip("/") + "/v1/repositories/{}/tags/{}".format(ImageName, tag) if version == 1 else url.strip("/") + "/v2/{}/tags/list".format(ImageName)
            logger.info("_get_imageId for url {}".format(ReqUrl))
            try:
                ImageId = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
                #result = requests.delete(ReqUrl, timeout=self.timeout, verify=self.verify).json()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                return ImageId
        return

    def _get_imageId_info(self, ImageId, url, version=1):
        """ 查询某个镜像的信息 """

        if url:
            ReqUrl = url.strip("/") + "/v1/images/{}/json".format(ImageId) if version == 1 else url.strip("/") + "/v2/{}/tags/xxx".format(ImageName)
            logger.info("_get_imageId_info for url {}".format(ReqUrl))
            try:
                ImageInfo = requests.get(ReqUrl, timeout=self.timeout, verify=self.verify).json()
            except Exception,e:
                logger.error(e, exc_info=True)
            else:
                return ImageInfo
        return {}

class MultiRegistryManager(BASE_REGISTRY_API):


    def __init__(self, timeout=2, verify=False):
        self.timeout = timeout
        self.verify  = verify        
        self._BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._dir0   = os.path.join(self._BASE, 'logs', ".Registries.db")
        self._dir1   = os.path.join(self._BASE, 'logs', ".ActiveRegistry.db")
        self._registries  = self._unpickle
        self._active      = self._unpickleActive

    def _pickle(self, data):
        """ 序列化所有数据写入存储 """
        try:
            with open(self._dir0, "w") as f:
                json.dump(data, f)
        except Exception,e:
            logger.error(e, exc_info=True)
            res = False
        else:
            res = True

        logger.info("pickle registries data, content is %s, write result is %s" %(data, res))
        return res

    @property
    def _unpickle(self):
        """ 反序列化信息取出所有数据 """
        try:
            with open(self._dir0, "r") as f:
                    data = json.load(f)
        except Exception,e:
            logger.warn(e, exc_info=True)
            res = []
        else:
            res = data or []

        logger.info("unpickle registries data is %s" %res)
        return res

    def _pickleActive(self, data):
        """ 序列化活跃仓库数据写入存储 """
        try:
            with open(self._dir1, "w") as f:
                json.dump(data, f)
        except Exception,e:
            logger.error(e, exc_info=True)
            res = False
        else:
            res = True

        logger.info("pickle active data, content is %s, write result is %s" %(data, res))
        return res

    @property
    def _unpickleActive(self):
        """ 反序列化信息取出活跃仓库 """
        try:
            with open(self._dir1, "r") as f:
                data = json.load(f)
        except Exception,e:
            logger.warn(e, exc_info=True)
            res = {}
        else:
            res = data or {}

        logger.info("unpickle active data is %s" %res)
        return res

    @property
    def getMember(self):
        """ 查询所有仓库名称 """
        return [ _.get("name") for _ in self._registries ]

    def isMember(self, name):
        """ 查询某name的仓库是否在存储中 """
        return name in self.getMember

    def getOne(self, name):
        """ 查询某name的仓库信息 """

        if self.isMember(name):
            return ( _ for _ in self._registries if _.get("name") == name ).next()
        else:
            logger.warn("no such registry named {}, return an empty dict".format(name))
            return {}

    @property
    def getActive(self):
        """ 查询活跃仓库 """
        return self._active

    def isActive(self, name):
        """ 判断某name的仓库是否为活跃仓库 """
        return name == self.getActive.get("name")

    def setActive(self, name):
        """ 设置活跃仓库 """
        logger.info("setActive, request name that will set is %s" % name)

        if self.isActive(name):
            logger.info("The name of the request is already active, think it successfully")
        else:
            logger.info("The name of the request is not current active registry, will update it to be active.")
            self._active = self.getOne(name)
            self._pickleActive(self._active)
            if self.isActive(name):
                logger.info("setActive, the request name sets it for active, successfully")
            else:
                logger.info("setActive, the request name sets it for active, but fail")
                return False
        return True

    def getRegistries(self):
        """ 查询所有仓库信息 """
        return self._registries

    def GET(self, query, state=False):
        """ 查询 """

        res = {"msg": None, "code": 0}
        logger.info("GET: the query params is {}".format(query))

        if not isinstance(query, (str, unicode)) or not query:
            res.update(msg="GET: query params type error or none", code=10000)
        else:
            query = query.lower()
            if query == "all":
                res.update(data=self.getRegistries())
            elif query == "active":
                res.update(data=self.getActive)
            elif query == "member":
                res.update(data=self.getMember)
            else:
                if self.isMember(query):
                    res.update(data=self.getOne(query))
                else:
                    res.update(msg="No such registry", code=10001)

        logger.info(res)
        return res

    def POST(self, name, addr, version=1, auth=None):
        """ 创建 """

        res  = {"msg": None, "code": 0}
        try:
            version = int(version)
        except Exception,e:
            logger.error(e, exc_info=True)
            res.update(msg="params error", code=-10002)
            logger.info(res)
            return res
        else:
            logger.info("post a registry, name is %s, addr is %s, version is %s" %(name, addr, version))

        if not name or not addr:
            res.update(msg="params error", code=10002)
        elif not "http://" in addr and not "https://" in addr:
            res.update(msg="addr params error, must be a qualified URL(include protocol)", code=10003)
        elif self.isMember(name):
            res.update(msg="registry already exists", code=10004)
        else:
            self._registries.append(dict(name=name, addr=addr, version=version, auth=auth))
            self._pickle(self._registries)
            res.update(success=True, code=0)
            logger.info("check all pass and added")

        logger.info(res)
        return res

    def DELETE(self, name):
        """ 删除当前存储中的私有仓 """

        res = {"msg": None, "code": 0, "success": False}
        logger.info("the name that will delete is %s" %name)

        if name in ("member", "active", "all"):
            res.update(msg="name reserved for the system key words", code=10005)

        elif self.isActive(name):
            res.update(msg="not allowed to delete the active cluster", code=10006)

        elif self.isMember(name):
            registry = self.getOne(name)
            logger.info("Will delete registry is %s" %registry)
            self._registries.remove(registry)
            if self.isMember(name):
                logger.info("Delete fail")
                res.update(success=False)
            else:
                logger.info("Delete successfully, pickle current registries")
                self._pickle(self._registries)
                res.update(success=True)

        else:
            res.update(msg="This registry does not exist", code=10007)

        logger.info(res)
        return res

    def PUT(self, name, setActive=False):
        """ 设置活跃仓库 """

        res = {"msg": None, "code": 0}
        logger.info("PUT request, setActive(%s), will set %s as active" %(setActive, name))

        if setActive:
            if name and self.isMember(name):
                res.update(success=self.setActive(name))
            else:
                res.update(msg="setActive, but no name param or name non-existent", code=10008)
        else:
            pass

        logger.info(res)
        return res

class ApiRegistryManager(BASE_REGISTRY_API):


    def __init__(self, timeout=2, verify=False, ActiveRegistry={}):
        self.timeout = timeout
        self.verify  = verify
        self._addr   = ActiveRegistry.get("addr")
        self._ver    = ActiveRegistry.get("version")
        self._auth   = ActiveRegistry.get("auth")
        logger.info("Registry API Init, registry is {}".format(self._addr))

    @property
    def url(self):
        """ 返回私有仓地址 """
        return self._addr

    @property
    def version(self):
        """ 返回私有仓版本 """
        return self._ver

    @property
    def isHealth(self):
        """ 返回私有仓健康状态 """
        return self._checkStatus(self.url, self.version)

    def list_repository(self, q=""):
        """ 查询私有仓镜像名称(默认列出所有镜像) """
        return self._search_all_repository(url=self.url, version=self.version, q=q)

    def list_imageTags(self, ImageName):
        """ 查询某镜像的tag列表 """
        return self._list_image_tags(url=self.url, version=self.version, ImageName=ImageName)

    def get_tag_info(self, ImageId):
        """ 查询某tag(ImageId)的镜像信息 """
        return self._get_imageId_info(url=self.url, version=self.version, ImageId=ImageId)
