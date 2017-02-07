# -*- coding:utf-8 -*-
#
# SetDate: 2017-02
# WebSite: www.saintic.com
#

from flask import Flask, request, g, jsonify, redirect, url_for
from utils.public import logger, gen_requestId
from config import GLOBAL
from ui import ui_blueprint
from api import api_blueprint
from libs.Registry import MultiRegistryManager, ApiRegistryManager

__version__ = '0.1'
__author__  = 'Mr.tao'
__email__   = 'staugur@saintic.com'
__doc__     = 'Multi Center and Multi Version Docker Registry Management UI.'

app = Flask(__name__)
app.register_blueprint(ui_blueprint, url_prefix="/ui")
app.register_blueprint(api_blueprint, url_prefix="/api")
registries = MultiRegistryManager()

#每个URL请求之前，定义初始化时间、requestId等相关信息并绑定到g.
@app.before_request
def before_request():
    g.auth      = True
    g.requestId = gen_requestId()
    g.registries= registries
    g.registry  = ApiRegistryManager(ActiveRegistry=g.registries.getActive)
    g.sysInfo   = {"Version": __version__, "Author": __author__, "Email": __email__, "Doc": __doc__}
    logger.info("Start Once Access, and this requestId is {}".format(g.requestId))

#每次返回数据中，带上响应头，包含本次请求的requestId，以及允许所有域跨域访问API, 记录访问日志.
@app.after_request
def add_header(response):
    response.headers["X-SaintIC-Request-Id"]   = g.requestId
    logger.info({
            "AccessLog": True,
            "status_code": response.status_code,
            "method": request.method,
            "ip": request.headers.get('X-Real-Ip', request.remote_addr),
            "url": request.url,
            "referer": request.headers.get('Referer'),
            "agent": request.headers.get("User-Agent"),
            "requestId": g.requestId
    })
    return response

@app.route("/")
def index():
    return redirect(url_for("ui.index"))

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'code': 404,
        'msg': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.errorhandler(403)
def Permission_denied(error=None):
    message = {
        "msg": "Authentication failed, permission denied.",
        "code": 403
    }
    return jsonify(message), 403

if __name__ == '__main__':
    Host  = GLOBAL.get('Host')
    Port  = GLOBAL.get('Port')
    Debug = GLOBAL.get('Debug', True)
    app.run(host=Host, port=int(Port), debug=Debug)
