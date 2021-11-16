# -*- coding: utf-8 -*-
"""
    views.api
    ~~~~~~~~~

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

from flask import Blueprint, g, request, jsonify
from config import GLOBAL, SITE
from libs import MultiRegistryRESTAPI, V2API
from utils.tool import new_res
from utils.exceptions import ApiError

bp = Blueprint("api", __name__)
mrm = MultiRegistryRESTAPI(db_dir=SITE["PersistentDirectory"])


@bp.before_request
def before_api():
    g.ar = V2API.genObj(mrm.getActive)


@bp.route("/")
def index():
    return jsonify(
        "Hello %s" % ("user" if g.signin else GLOBAL["ProcessName"])
    )


@bp.route("/registries", methods=["GET", "POST", "PUT", "DELETE"])
def registries():
    if request.method == "GET":
        """查询存储的私有仓库信息"""
        query = request.args.get("q")
        return mrm.GET(query)

    elif request.method == "POST":
        """向存储里添加一个私有仓库"""
        addr = request.form.get("addr")
        auth = request.form.get("auth")
        name = request.form.get("name")
        return mrm.POST(addr, auth, name)

    elif request.method == "PUT":
        """设置活跃仓库"""
        action = request.args.get("action", request.form.get("action"))
        name = request.args.get("name", request.form.get("name"))
        if action == "setActive":
            return mrm.PUT_SetActive(name)

    elif request.method == "DELETE":
        """删除当前存储中的私有仓"""
        name = request.form.get("name")
        return mrm.DELETE(name)


@bp.route("/registry", methods=["GET", "DELETE"])
def registry():
    if request.method == "GET":
        query = request.args.get("q")
        name = request.args.get("name")
        tag = request.args.get("tag")

        res = new_res()

        if query == "url":
            res.update(url=g.ar.url)

        elif query == "status":
            res = g.ar.check_status()

        elif query == "all_repository":
            res = g.ar.list_repository()

        elif query == "all_tag":
            if not name:
                raise ApiError("invalid name param")
            res = g.ar.list_image_tags(name)

        elif query == "tag_info":
            if not name or not tag:
                raise ApiError("invalid name or tag param")
            res = g.ar.get_minifests(name, tag)

        else:
            if query:
                res = g.ar.list_repository(q=query)
            else:
                raise ApiError("Invalid query")
        return res

    elif request.method == "DELETE":
        ImageName = request.form.get("ImageName")
        ImageTag = request.form.get("ImageTag")

        if ImageTag:
            return g.ar._delete_imageTag(ImageName=ImageName, tag=ImageTag)
        else:
            return g.ar.delete_image(ImageName=ImageName)
