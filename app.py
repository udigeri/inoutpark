from flask import Flask
from flask import render_template
from flask import url_for
from flask import flash

from flask_qrcode import QRcode

from models import db

host_name = "localhost"
database = "postgres"
username = "hudak.pavol"
pwd = ""
port_id = 5432

flask_app = Flask(__name__)

flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/postgres'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

qrcode = QRcode(flask_app)

db.init_app(flask_app)

with flask_app.app_context():
    db.create_all()



@flask_app.route("/")
def index():
    flash("Successfull", "success")
    return render_template("index.jinja")

@flask_app.errorhandler(404)
@flask_app.errorhandler(500)
def not_found(error):
    return render_template("error.jinja", error=error), error.code

@flask_app.route("/customer")
def customer():
    return render_template("customer.jinja")

@flask_app.route("/carts/", methods=["GET"])
def viewCarts():
    return "List of carts"

@flask_app.route("/carts/<uuid:id>")
def viewCartId(id):
    url = url_for("viewCarts") + f'{id}'
    return render_template("customer.jinja", uuid=id, qr=qrcode(f'{url}'), url=url)

@flask_app.route("/lpns/", methods=["GET"])
def viewLPNs():
    return "List of LPNs"

@flask_app.route("/lpns/<string:lpn>")
def viewLpnId(lpn):
    return f"LPN: {lpn}"

