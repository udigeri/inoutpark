from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import flash

from flask_qrcode import QRcode

from models import db
from models import Tenants
from models import Carts


flask_app = Flask(__name__)

flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/postgres'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

qrcode = QRcode(flask_app)

def init_db(self):
    with flask_app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(filldb_default_tenant(self))
        db.session.add(filldb_default_cart(self))
        db.session.commit()


def filldb_default_tenant(self):
        return Tenants(name="InOut Park",
        company="Scheidt&Bachmann Slovensko s.r.o",
        street="Priemyselná 14",
        city="Žilina",
        zip="01004",
        country="Slovakia",
        schema="sk_inoutpark",
        production=0,
        suspend=0)

def filldb_default_cart(self):
        return Carts(epan="02491012010011033016399610",
        lpn="ZA123AZ",
        amount=2305,
        currency="EUR",
        entryTime="06.02.2023 10:13:45",
        authorizeTime="06.02.2023 11:25:45",
        exitTime="06.02.2023 11:26:50")

def getFormattedAmount(self, amount):
    return '{}.{:0<2}'.format(int(amount/100), int(amount%100) )



db.init_app(flask_app)



@flask_app.route("/")
def index():
    tenants = Tenants.query.filter_by(id = 1).first()
    return render_template("index.jinja", tenant=tenants)

@flask_app.errorhandler(404)
@flask_app.errorhandler(500)
def not_found(error):
    tenants = Tenants.query.filter_by(id = 1).first()
    return render_template("error.jinja", tenant=tenants, error=error), error.code

@flask_app.route("/customer")
def customer():
    return render_template("customer.jinja")

@flask_app.route("/carts/", methods=["GET"])
def viewCarts():
    return "List of carts"

@flask_app.route("/carts/<uuid:id>")
def viewCartId(id):
    url = url_for("viewCarts") + f'{id}'
    tenants = Tenants.query.filter_by(id = 1).first()
    return render_template("customer.jinja", tenant=tenants, uuid=id, qr=qrcode(f'{url}'), url=url)

@flask_app.route("/lpns/", methods=["POST"])
def viewLpn():
    tenants = Tenants.query.filter_by(id = 1).first()
    carts = None
    if len(request.form['lpn']) > 0:
        carts = Carts.query.filter_by(lpn = request.form['lpn']).first()
        if carts != None:
            flash("Successfull", "success")

    return render_template("lpn.jinja", tenant=tenants, cart=carts)

@flask_app.route("/lpns/<string:lpn>", methods=["GET"])
def viewLpnId(lpn):
    tenants = Tenants.query.filter_by(id = 1).first()
    #url = url_for("viewCarts") + f'{id}'
    return render_template("lpn.jinja", tenant=tenants)

