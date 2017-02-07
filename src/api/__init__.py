# -*- coding: utf8 -*-

from flask import Blueprint, request, g
from flask_restful import Api, Resource
from utils.public import logger

class Registries(Resource):

    def get(self):
        """ 查询存储的私有仓库信息 """

        query  = request.args.get("query")
        state  = True if request.args.get("state", False) in ('true', 'True', True) else False
        return g.registries.GET(query, state)

    def post(self):
        """ 向存储里添加一个私有仓库 """

        name = request.form.get("name")
        addr = request.form.get("addr")
        auth = request.form.get("auth")
        version = request.form.get("version", 1)
        return g.registries.POST(name=name, addr=addr, version=version, auth=auth)

    def put(self):
        """ 设置活跃仓库 """

        name = request.args.get("name")
        setActive = True if request.args.get("setActive") in ("true", "True", True) else False
        return g.registries.PUT(name=name, setActive=setActive)

    def delete(self):
        """ 删除存储中的一个私有仓库 """

        name = request.form.get("name")
        return g.registries.DELETE(name)

class Registry(Resource):

    def get(self):
        """ 查询私有仓 """

        query     = request.args.get("q")
        ImageName = request.args.get("ImageName")
        ImageId   = request.args.get("ImageId")
        tag       = request.args.get("tag")

        if g.auth:
            res = {"msg": None, "data": None}
            if query == "url":
                res.update(data=g.registry.url)
            elif query == "status":
                res.update(data=g.registry.status)
            elif query == "version":
                res.update(data=g.registry.version)
            elif query == "all_repository":
                res.update(data=g.registry._list_all_repository)
            elif query == "all_tag":
                res.update(data=g.registry._list_repository_tag(ImageName))
            elif query == "all_imageId_ancestry":
                res.update(data=g.registry._list_imageId_ancestry(ImageId))
            elif query == "imageId_info":
                res.update(data=g.registry._get_imageId_info(ImageId))
            logger.info(res)
            return res
        else:
            return abort(403)

    def delete(self):
        """ 删除镜像<标签> """

        repository_name     = request.args.get("repository_name")
        repository_name_tag = request.args.get("repository_name_tag")

        if g.auth:
            res = {"msg": None, "success": False}
            if repository_name_tag:
                res.update(success=g.registry._delete_repository_tag(ImageName=repository_name, tag=repository_name_tag))
            else:
                res.update(success=g.registry._delete_repository(ImageName=repository_name))
            logger.info(res)
            return res
        else:
            return abort(403)


api_blueprint = Blueprint(__name__, __name__)
api = Api(api_blueprint)
api.add_resource(Registries, '/registries', '/registries/', endpoint='registries')
api.add_resource(Registry, '/registry', '/registry/', endpoint='registry')

