# -*- coding: utf-8 -*-
"""
    Breezes
    ~~~~~~~

    Docker registry v2 web interface.

    :copyright: (c) 2021 by Hiroshi.tao.
    :license: Apache 2.0, see LICENSE for more details.
"""

from flask import Flask, g, jsonify, request, render_template
from config import SITE
from views import ui_blueprint, api_blueprint
from utils.tool import logger, JsonResponse, uri_path_join
from utils.exceptions import ApiError

__version__ = "0.2"
__author__ = "Hiroshi.tao"
__doc__ = "Multi Center Docker Registry Management UI."

app = Flask(__name__)
app.response_class = JsonResponse

app.register_blueprint(
    ui_blueprint,
    url_prefix=uri_path_join(SITE["URIPrefix"], "ui"),
)
app.register_blueprint(
    api_blueprint,
    url_prefix=uri_path_join(SITE["URIPrefix"], "api"),
)

# from libs import MultiRegistryManager, V2API
# multi_reg_manager = MultiRegistryManager(db_dir=SITE["PersistentDirectory"])


@app.context_processor
def GlobalTemplateVariables():
    return {
        "Version": __version__,
    }


@app.before_request
def before_request():
    g.signin = True
    print(app.url_map)
    # g.mrm = multi_reg_manager
    # g.registry = V2API.getActiveObj(g.mrm.getActive)


@app.errorhandler(500)
@app.errorhandler(405)
@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(413)
@app.errorhandler(400)
def handle_error(e):
    if getattr(e, "code", None) == 500:
        logger.error(e, exc_info=True)
    code = e.code
    name = e.name
    if "/api/" in request.path:
        return jsonify(dict(msg=name, code=code)), code
    else:
        return name
        return render_template("error.html", code=code, name=name), code


@app.errorhandler(ApiError)
def handle_api_error(e):
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response
