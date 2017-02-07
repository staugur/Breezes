# -*- coding:utf-8 -*-

from flask import Blueprint, render_template

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')

@ui_blueprint.route("/")
def index():
    return render_template("registry/index.html")

@ui_blueprint.route("/registry/")
def registry():
    return render_template("registry/registry.html")

@ui_blueprint.route("/registry/<namespace>/<repository_name>/")
def registryImageName(namespace, repository_name):
    return render_template("registry/imageName.html", imageName="{}/{}".format(namespace, repository_name))

@ui_blueprint.route("/registry/<imageId>")
def registryImageId(imageId):
    return render_template("registry/imageId.html", imageId=imageId)

@ui_blueprint.route("/registry/add/")
def registry_add():
    return render_template("registry/registry_add.html")
