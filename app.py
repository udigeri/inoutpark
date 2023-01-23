from flask import Flask
from flask import render_template
from flask import url_for

flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return render_template("index.jinja")

@flask_app.route("/paid")
def paid():
    return render_template("paid.jinja")

@flask_app.route("/carts/", methods=["GET"])
def viewCarts():
    return "List of carts"

@flask_app.route("/carts/<uuid:id>")
def viewCartId(id):
    return f"cartId info: {id}"

@flask_app.route("/lpns/", methods=["GET"])
def viewLPNs():
    return "List of LPNs"

@flask_app.route("/lpns/<string:lpn>")
def viewLpnId(lpn):
    return f"LPN: {lpn}"

