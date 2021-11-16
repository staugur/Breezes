# -*- coding: utf-8 -*-
"""
    libs.registries
    ~~~~~~~~~~~~~~~

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

import json
from os import mkdir
from os.path import dirname, abspath, isdir, join
from urllib.parse import urlparse
from typing import NewType, List, Dict, Optional, Union
from utils.tool import logger, ApiResType, new_res, E
from utils.exceptions import ApiError
from .v2 import V2API

__all__ = ["MultiRegistryManager"]

#: 内部数据类型
RepoType = Dict[str, Union[str, int, bool]]
ReposType = NewType("ReposType", List[RepoType])


class MultiRegistryManager(object):
    """管理多个私有仓信息"""

    def __init__(self, db_dir: Optional[str] = None):
        self._db_dir: str = db_dir
        if not self._db_dir:
            self._db_dir = join(dirname(dirname(abspath(__file__))), ".db")
        if not isdir(self._db_dir):
            mkdir(self._db_dir)
        self._rsdb: str = join(self._db_dir, "Registries.db")
        self._ardb: str = join(self._db_dir, "ActiveRegistry.db")
        self._registries: ReposType = self._unpickle()
        self._active: RepoType = self._unpickleActive()

    def _pickle(self) -> bool:
        """序列化所有数据写入存储"""
        try:
            with open(self._rsdb, "w") as f:
                json.dump(self._registries, f)
        except ValueError as e:
            logger.error(e, exc_info=True)
            return False
        else:
            return True

    def _unpickle(self) -> ReposType:
        """反序列化信息取出所有数据"""
        try:
            with open(self._rsdb, "r") as f:
                data = json.load(f)
        except (ValueError, FileNotFoundError) as e:
            logger.warn(e)
            return []
        else:
            return data or []

    def _pickleActive(self) -> bool:
        """序列化活跃仓库数据写入存储"""
        try:
            with open(self._ardb, "w") as f:
                json.dump(self._active, f)
        except ValueError as e:
            logger.error(e, exc_info=True)
            return False
        else:
            return True

    def _unpickleActive(self) -> RepoType:
        """反序列化信息取出活跃仓库"""
        try:
            with open(self._ardb, "r") as f:
                data = json.load(f)
        except (ValueError, FileNotFoundError) as e:
            logger.warn(e)
            return {}
        else:
            return data or {}

    def getRegistries(self) -> ReposType:
        """查询所有仓库信息"""
        return self._registries

    def getNames(self) -> List[str]:
        """查询所有仓库名称"""
        return [_.get("name") for _ in self.getRegistries()]

    def isMember(self, name: str) -> bool:
        """查询某name的仓库是否在存储中"""
        return name in self.getNames()

    def getOne(self, name: str) -> Optional[RepoType]:
        """查询某name的仓库信息"""
        if self.isMember(name):
            return next(
                (_ for _ in self.getRegistries() if _.get("name") == name)
            )

    @property
    def getActive(self) -> RepoType:
        """查询活跃仓库"""
        return self._active

    def isActive(self, name: str) -> bool:
        """判断某name的仓库是否为活跃仓库"""
        return name == self.getActive.get("name")

    def setActive(self, name: str) -> bool:
        """设置活跃仓库"""
        if not self.isActive(name):
            data = self.getOne(name)
            if data and isinstance(data, dict):
                self._active = data
                self._pickleActive()
        return self.isActive(name)

    def isHealth(self, name) -> bool:
        """返回私有仓状态"""
        data = self.getOne(name)
        if data and isinstance(data, dict):
            obj = V2API.genObj(data)
            res = obj.check_status()
            if E not in res:
                return True
        return False


class MultiRegistryRESTAPI(MultiRegistryManager):
    def GET(self, query: str) -> ApiResType:
        """查询"""

        if not query:
            raise ApiError("invalid query param")

        query = query.lower()
        res = new_res()

        if query == "_all":
            res.update(data=self.getRegistries())
        elif query == "_active":
            res.update(data=self.getActive)
        elif query == "_names":  # member
            res.update(data=self.getNames())
        else:
            #: query with name
            if self.isMember(query):
                res.update(data=self.getOne(query))
            else:
                res[E] = "No such registry"

        return res

    def POST(
        self,
        addr: str,
        auth: Optional[str] = None,
        name: Optional[str] = None,
    ) -> ApiResType:
        """添加私有仓"""

        if not addr:
            raise ApiError("the addr param is required")
        if not "http://" in addr and not "https://" in addr:
            raise ApiError("invalid addr param")

        if not name:
            name = urlparse(addr).netloc
        if self.isMember(name):
            raise ApiError("registry already exists")

        self._registries.append(
            dict(
                name=name.strip().lower(),
                addr=addr.strip().lower(),
                version=2,
                auth=auth or "",
            )
        )
        return dict(success=self._pickle())

    def DELETE(self, name: str) -> ApiResType:
        """删除当前存储中的私有仓"""

        if not name:
            raise ApiError("invalid name param")

        if name.startswith("_"):
            raise ApiError("name reserved for the system key words")

        if self.isActive(name):
            raise ApiError("not allowed to delete the active cluster")

        res = new_res()
        if self.isMember(name):
            registry = self.getOne(name)
            self._registries.remove(registry)
            res.update(success=self._pickle())
        else:
            res[E] = "This registry does not exist"

        return res

    def PUT_SetActive(
        self,
        name: str,
    ) -> ApiResType:
        """设置活跃仓库"""
        res = new_res()

        if name and self.isMember(name):
            res.update(success=self.setActive(name))
        else:
            res[E] = "invalid name param or name non-existent"

        return res
