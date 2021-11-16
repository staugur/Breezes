# -*- coding: utf-8 -*-
"""
    libs.v2
    ~~~~~~~

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

from utils.tool import logger, try_request, ApiResType, new_res, E
from requests import Response, RequestException
from typing import List, Optional, Dict, Any

__all__ = ["V2API"]

#: V2 Accept类型
V2MediaType: str = "application/vnd.docker.distribution.manifest.v2+json"
FatMediaType: str = "application/vnd.docker.distribution.manifest.list.v2+json"
#: 默认错误
DftErr: str = "request error"


def regresformat(resp: Dict[str, List[Dict[str, str]]]) -> ApiResType:
    """registry v2 api response format:
    {
        "errors:" [
            {
                "code": <error identifier>,
                "message": <message describing condition>,
                "detail": <unstructured>
            },
        ...
        ]
    }
    """
    if isinstance(resp, dict) and E in resp:
        errs = resp.pop(E)
        if errs and isinstance(errs, list):
            logger.warn(errs)
            codes = [
                err["code"]
                for err in errs
                if isinstance(err, dict) and "code" in err
            ]
            resp[E] = ",".join(codes)
        else:
            resp[E] = "invalid errors content"
    return resp


class V2API(object):
    """私有仓v2接口封装"""

    def __init__(self, url: str, auth: Optional[str], verify: bool = False):
        self._base_url = url
        self._auth = auth
        self._verify = verify

    def __http(
        self,
        uri: str,
        method: str = "get",
        data: Optional[Dict[str, Any]] = None,
        mediaType: str = None,
    ) -> Optional[Response]:
        headers = {"Accept": mediaType if mediaType else V2MediaType}
        try:
            return try_request(
                f"{self._base_url.rstrip('/')}/{uri.lstrip('/')}",
                data=data,
                headers=headers,
                method=method,
                verify=self._verify,
            )
        except RequestException as e:
            logger.error(e)

    def check_status(self) -> ApiResType:
        """返回私有仓状态"""
        res = new_res()
        req = self.__http("/v2/")
        if req:
            if req.status_code == 200:
                res.update(ping="pong")
            else:
                res.update(regresformat(req.json()))
        else:
            res[E] = DftErr
        return res

    def list_repository(self) -> ApiResType:
        """列出私有仓所有镜像"""
        res = new_res()
        req = self.__http("/v2/_catalog")
        if req:
            res.update(regresformat(req.json()))
        else:
            res[E] = DftErr
        return res

    def _search_repository(self, q=""):
        """搜索私有仓所有镜像"""
        res = self.list_repository()
        if E in res:
            return res
        else:
            return dict(
                repositories=[n for n in res["repositories"] if q in n]
            )

    def list_image_tags(self, ImageName: str) -> ApiResType:
        """列出某个镜像所有标签"""
        res = new_res()
        req = self.__http(f"/v2/{ImageName}/tags/list")
        if req:
            data = regresformat(req.json())
            print(data)
            res.update(
                name=data["name"],
                tags={
                    tag: self._get_digest(ImageName, tag)
                    for tag in data.get("tags", [])
                },
            )
        else:
            res[E] = DftErr
        return res

    def _get_digest(self, ImageName: str, tag: str) -> str:
        """查询某个镜像tag的digest"""
        if ImageName and tag:
            req = self.__http(
                f"/v2/{ImageName}/manifests/{tag}",
                mediaType=FatMediaType,
                method="head",
            )
            if req:
                return req.headers.get("Docker-Content-Digest", "")
        return ""

    def get_minifests(self, ImageName: str, reference: str):
        """查询镜像清单"""
        res = new_res()
        req = self.__http(
            f"/v2/{ImageName}/manifests/{reference}", mediaType=FatMediaType
        )
        if req:
            res.update(regresformat(req.json()))
        else:
            res[E] = DftErr
        return res

    def delete_image(self, ImageName, url, version=1):
        """删除一个镜像"""
        res = {"msg": None, "success": False}
        return res
        if url:
            ReqUrl = (
                url.strip("/") + "/v1/repositories/{}/".format(ImageName)
                if version == 1
                else ""
            )
            logger.info("_delete_image for url {}".format(ReqUrl))
            try:
                delete_repo_result = requests.delete(
                    ReqUrl, timeout=self.timeout, verify=self.verify
                ).json()
            except Exception as e:
                logger.error(e, exc_info=True)
                if version == 1:
                    res.update(msg=e)
                else:
                    res.update(msg="The operation is unsupported.", code=-1)
            else:
                res.update(success=delete_repo_result)
        logger.info(res)
        return res

    def _delete_imageTag(self, ImageName, tag, url, version=1):
        """删除一个镜像标签"""

        res = {"msg": None, "success": False}
        return res
        if url:
            ReqUrl = (
                url.strip("/")
                + "/v1/repositories/{}/tags/{}".format(ImageName, tag)
                if version == 1
                else url.strip("/")
                + "/v2/{}/manifests/{}".format(
                    ImageName,
                    self._from_image_tag_getId(ImageName, tag, url, version),
                )
            )
            logger.info("_delete_imageTag for url {}".format(ReqUrl))
            try:
                delete_repo_result = requests.delete(
                    ReqUrl, timeout=self.timeout, verify=self.verify
                ).json()
            except Exception as e:
                logger.error(e, exc_info=True)
                res.update(msg=e)
            else:
                if version == 1:
                    res.update(success=delete_repo_result)
                else:
                    res.update(msg="The operation is unsupported.", code=-1)
        logger.info(res)
        return res

    @property
    def url(self):
        return self._base_url

    @property
    def isHealth(self) -> bool:
        """返回私有仓状态"""
        res = self.check_status()
        if E not in res:
            return True
        return False

    @staticmethod
    def genObj(options: Dict[str, str]) -> Optional["V2API"]:
        if options and isinstance(options, dict):
            _addr = options["addr"]
            _auth = options.get("auth")
            return V2API(_addr, _auth, False)
