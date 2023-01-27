from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import flash

from flask_qrcode import QRcode
from datetime import datetime

from models import db
from models import Tenants
from models import Carts
from models import Pgscarts



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
        db.session.add(filldb_default_pgscart(self))
        db.session.commit()


def filldb_default_tenant(self):
    return Tenants(name="InOut Park",
        company="Scheidt&Bachmann Slovensko s.r.o",
        street="Priemyselná 14",
        city="Žilina",
        zip="01001",
        country="Slovakia",
        schema="sk_inoutpark",
        production=0,
        suspend=0)

def filldb_default_cart(self):
    return Carts(
        epan="02491012010011033016399610",
        lpn="ZA123AZ",
        amount=700,
        currency="EUR",
        entryTime="02.26.2023 13:15:45",
        authorizeTime="03.18.2023 15:25:35",
        exitTime="03.18.2023 15:26:50"
        )

def filldb_default_pgscart(self):
    cart = Carts.query.all()

    return Pgscarts(
        carts_id = cart[0].id,
        payShcId="12345678-1234-5678-1234-123456789012",
        payAmount=700,
        payCurrency="EUR",
        payTime="03.18.2023 15:26:00",
        payId="C-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        payMediaId="456789 **** 1234",
        payMediaType="Visa",
        payStatus=0
        )

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



@flask_app.route("/carts/add", methods=["GET"])
def addCarts():
    db.session.add(Carts())
    db.session.commit()
    return "New carts created - OK"



@flask_app.route("/carts/<uuid:uuid>")
def viewCartId(uuid):
    tenants = Tenants.query.filter_by(id = 1).first()
    carts = Carts.query.filter_by(id = uuid).first()
    if carts.epan != None and carts.amount != None:
        url = url_for("viewCartId", uuid=uuid)
        print (url)
        return render_template("pay.jinja", tenant=tenants, cart=carts)#, qr=qrcode(f'{url}'), url=url)
    else:
        args = request.args
        carts.updated = datetime.utcnow()
        carts.epan = args.get("epan")
        carts.lpn = args.get("lpn")
        carts.amount = args.get("amount")
        carts.currency = args.get("currency")
        carts.entryTime = "01.01.1977 00:00:00"
        carts.authorizeTime = "01.01.1977 00:00:00"
        db.session.commit()
        return render_template("cart.jinja", tenant=tenants, cart=carts)




@flask_app.route("/lpns/", methods=["POST"])
def viewLpn():
    tenants = Tenants.query.filter_by(id = 1).first()
    lpn = None
    carts = None
    if len(request.form['lpn']) > 0:
        carts = Carts.query.filter_by(lpn = request.form['lpn']).first()
        if carts != None:
            lpn = carts.lpn
            flash("Successfull", "success")
        else:
            flash("Failed", "fail")

    return render_template("lpn.jinja", tenant=tenants, cart=carts, lpn=lpn)



@flask_app.route("/lpns/<string:lpn>", methods=["GET"])
def viewLpnId(lpn):
    tenants = Tenants.query.filter_by(id = 1).first()
    carts = None
    if len(lpn) > 0:
        carts = Carts.query.filter_by(lpn = lpn).first()
        if carts != None:
            flash("Successfull", "success")
        else:
            flash("Failed", "fail")
    return render_template("lpn.jinja", tenant=tenants, cart=carts, lpn=lpn)

