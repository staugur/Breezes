# -*- coding: utf-8 -*-
"""
    views.ui
    ~~~~~~~~

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

from flask import Blueprint, render_template, request, g
from libs import MultiRegistryManager,V2API
from config import SITE


bp = Blueprint(
    "ui",
    __name__,
    template_folder="templates",
    static_folder="assets",
    static_url_path="/assets",
)
mrm = MultiRegistryManager(db_dir=SITE["PersistentDirectory"])


@bp.before_request
def before_api():
    g.mrm = mrm
    g.ar = V2API.genObj(mrm.getActive)


@bp.route("/")
def index():
    return render_template("registry/index.html")


@bp.route("/registry/")
def registry():
    return render_template("registry/registry.html")


@bp.route("/registry/<namespace>/<repository_name>/")
def registryImageName(namespace, repository_name):
    return render_template(
        "registry/imageName.html",
        ImageName="{}/{}".format(namespace, repository_name).replace("_/", ""),
    )


@bp.route("/registry/<imageId>")
def registryImageId(imageId):
    return render_template(
        "registry/imageId.html",
        imageId=imageId,
        ImageName=request.args.get("ImageName"),
    )


@bp.route("/registry/add/")
def registry_add():
    return render_template("registry/registry_add.html")
