# -*- coding: utf8 -*-

from flask import Blueprint, request, g
from flask_restful import Api, Resource
from utils.public import logger

class Registries(Resource):

    def get(self):
        """ 查询存储的私有仓库信息 """

        query  = request.args.get("q")
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

        res       = {}
        query     = request.args.get("q")
        ImageName = request.args.get("ImageName")
        ImageId   = request.args.get("ImageId")

        if query == "url":
            res.update(data=g.registry.url)
        elif query == "status":
            res.update(data=g.registry.isHealth)
        elif query == "version":
            res.update(data=g.registry.version)
        elif query == "all_repository":
            res=g.registry.list_repository(q="")
        elif query == "all_tag":
            res=g.registry.list_imageTags(ImageName)
        elif query == "tag_info":
            res=g.registry.get_tag_info(ImageId, ImageName)
        else:
            if query:
                res=g.registry.list_repository(q=query)
            else:
                res.update(msg="Invalid query", code=-2)

        return res

    def delete(self):
        """ 删除镜像<标签> """

        ImageName= request.form.get("ImageName")
        ImageTag = request.form.get("ImageTag")
        logger.info("api registry delete, ImageName:{}, ImageTag:{}".format(ImageName, ImageTag))

        if ImageTag:
            return g.registry.delete_an_image_tag(ImageName=ImageName, tag=ImageTag)
        else:
            return g.registry.delete_an_image(ImageName=ImageName)

api_blueprint = Blueprint(__name__, __name__)
api = Api(api_blueprint)
api.add_resource(Registries, '/registries', '/registries/', endpoint='registries')
api.add_resource(Registry, '/registry', '/registry/', endpoint='registry')

