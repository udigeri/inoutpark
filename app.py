from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import flash
from flask import jsonify

from flask_qrcode import QRcode
from datetime import datetime
from requests.auth import HTTPBasicAuth
import json

from sqlalchemy import func
from models import db
from models import Tenants
from models import Carts
from models import Pgscarts
from rest import Restful
from transaction import Transaction


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
        base_url="http://192.168.71.164",
        schema="pgs-testCCV",
        production=0,
        suspend=0)

def filldb_default_cart(self):
    return Carts(
        updated=datetime.now(),
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
        payStatus=0,
        payDescription="OK"
        )

def get_shopping_cart(tenant, cart):
    featureURL = "http://localhost:8080/pgs/public/api/payment/paymentcart/{tenantName}".format(
        tenantName = tenant.schema
        )
    body = {"requestor": tenant.name, 
            "correlationId": f"{cart.id}",
            "amount": cart.amount,
            "currency": cart.currency,
            "reason": "Parking ticket",
            "reference": cart.epan,
            "successCallbackUrl": f"{tenant.base_url}/approved",
            "failureCallbackUrl": f"{tenant.base_url}/declined",
            "customStyle": "style=\"color:orange;\"",
            "tokenRequired": False
            }

    rest = Restful()
    resp = rest.put(featureURL, 
                    data=json.dumps(body), 
                    auth=HTTPBasicAuth("testexport", "testexport"))

    shoppingCartUuid = None
    if resp.status_code == 200:
        data = json.loads(resp.text)
        for key in data:
            if key == 'cartId':
                shoppingCartUuid = data[key]
    return shoppingCartUuid

def get_pay_methods(tenant, cart, shc):
    featureURL = "http://localhost:8080/pgs/public/api/payment/paymenttypes/{tenantName}/{cart}/{correlationId}/{requestor}/{locale}?costCenter={costCentre}&imageColor={imageColor}".format(
        tenantName=tenant.schema,
        cart=shc,
        correlationId=f"{cart.id}",
        requestor=tenant.name,
        locale="en-Gb",
        costCentre=2014615,
        imageColor=True,
        )

    rest = Restful()
    resp = rest.get(featureURL, 
                    data=None, 
                    auth=HTTPBasicAuth("testexport", "testexport"))

    trx = Transaction(cart.lpn, cart.lpn, cart.amount)
    if resp.status_code == 200:
        data = json.loads(resp.text)

        # mandatory fields
        trx.trx_methods = [y[z] for x in data for y in data[x] for z in y if x=='offeredPaymentTypes' if z=='name']
        trx.trx_urls = [y[z] for x in data for y in data[x] for z in y if x=='offeredPaymentTypes' if z=='formUrl']
        trx.trx_fees = [y[z] for x in data for y in data[x] for z in y if x=='offeredPaymentTypes' if z=='fee']
        # optional fields
        for i in range(len(trx.trx_methods)) :
            method = data['offeredPaymentTypes'][i]
            if (method['name'] == trx.trx_methods[i]):
                if 'imageUrl' in method:
                    trx.trx_imageUrls.append(method['imageUrl'])
                else:
                    trx.trx_imageUrls.append("../static/none.png")
                if 'isTokenizationPossible' in method:
                    trx.trx_possible_tokenization.append(method['isTokenizationPossible'])
                else:
                    trx.trx_possible_tokenization.append("False")

    return trx


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



@flask_app.route("/approved")
def pay_approved():
    shc = request.args.get("shoppingCartUuid")
    if shc != None:
        flash("APPROVED", "success")

        pgscarts = Pgscarts.query.filter_by(payShcId = shc).first()
        pgscarts.payTime = datetime.now()
        pgscarts.payId = request.args.get("payId")
        pgscarts.payMediaId = request.args.get("maskedMediaId")
        pgscarts.payMediaType = request.args.get("mediaType")
        pgscarts.payStatus = 0
        pgscarts.updated = pgscarts.payTime
        pgscarts.payDescription = "OK"
        db.session.commit()
    return redirect(url_for("viewCartId", uuid=pgscarts.carts_id))

@flask_app.route("/declined")
def pay_declined():
    shc = request.args.get("shoppingCartUuid")
    if shc != None:
        flash("DECLINED", "fail")

        pgscarts = Pgscarts.query.filter_by(payShcId = shc).first()
        pgscarts.payTime = datetime.now()
        pgscarts.payId = request.args.get("payId")
        pgscarts.payMediaId = request.args.get("maskedMediaId")
        pgscarts.payMediaType = request.args.get("mediaType")
        pgscarts.payStatus = 1
        pgscarts.updated = pgscarts.payTime
        pgscarts.payDescription = request.args.get("description")
        db.session.commit()
    return redirect(url_for("viewCartId", uuid=pgscarts.carts_id))


@flask_app.route("/carts/add", methods=["GET"])
def addCarts():
    cart = Carts()
    cart.entryTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.add(cart)
    db.session.commit()
    return f"<html>New cart <br><h3>{cart.id}</h3><br>created - OK</html>"



@flask_app.route("/carts/add", methods=["POST"])
def createCart():
    cart = Carts()
    cart.entryTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.add(cart)
    db.session.commit()
    return jsonify(
        cartId=cart.id,
        approveId=cart.approve_uuid,
        declineId=cart.decline_uuid,
    )



@flask_app.route("/carts/<uuid:uuid>", methods=["POST"])
def statusCart(uuid):
    tenants = Tenants.query.filter_by(id = 1).first()
    cart = Carts.query.filter_by(id = uuid).first()
    if cart == None:
        return jsonify(
            cartId=uuid,
            status="UNKNOWN",
        )
    else:
        if cart.pgs_id == None:
            return jsonify(
                cartId=cart.id,
                approveId=cart.approve_uuid,
                declineId=cart.decline_uuid,
                epan=cart.epan,
                lpn=cart.lpn,
                status="CREATED"
            )
        else:
            if cart.pgs_id.payStatus == 0:
                return jsonify(
                    cartId=cart.id,
                    approveId=cart.approve_uuid,
                    declineId=cart.decline_uuid,
                    epan=cart.epan,
                    lpn=cart.lpn,
                    payShcId=cart.pgs_id.payShcId,
                    payAmount=cart.pgs_id.payAmount,
                    payId=cart.pgs_id.payId,
                    payMediaId=cart.pgs_id.payMediaId,
                    payMediaType=cart.pgs_id.payMediaType,
                    payDescription=cart.pgs_id.payDescription,
                    status="APPROVED"
                )
            elif cart.pgs_id.payStatus == 1:
                return jsonify(
                    cartId=cart.id,
                    approveId=cart.approve_uuid,
                    declineId=cart.decline_uuid,
                    epan=cart.epan,
                    lpn=cart.lpn,
                    payShcId=cart.pgs_id.payShcId,
                    payAmount=cart.pgs_id.payAmount,
                    payId=cart.pgs_id.payId,
                    payMediaId=cart.pgs_id.payMediaId,
                    payMediaType=cart.pgs_id.payMediaType,
                    payDescription=cart.pgs_id.payDescription,
                    status="DECLINED"
                )
            elif cart.pgs_id.payStatus == 2:
                return jsonify(
                    cartId=cart.id,
                    approveId=cart.approve_uuid,
                    declineId=cart.decline_uuid,
                    epan=cart.epan,
                    lpn=cart.lpn,
                    status="PROCESSING"
                )



@flask_app.route("/carts/<uuid:uuid>", methods=["GET"])
def viewCartId(uuid):
    tenants = Tenants.query.filter_by(id = 1).first()
    carts = Carts.query.filter_by(id = uuid).first()
    if carts.pgs_id == None:
        if (carts.epan != None and carts.amount != None):
            shc = get_shopping_cart(tenants, carts)
            trx = get_pay_methods(tenants, carts, shc)
            pgsCart  = Pgscarts(
                updated=datetime.now(),
                carts_id = uuid,
                payShcId=shc,
                payAmount=carts.amount,
                payCurrency=carts.currency,
                # payTime="03.18.2023 15:26:00",
                # payId="C-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                # payMediaId="456789 **** 1234",
                # payMediaType="Visa",
                payStatus=2
                )
            db.session.add(pgsCart)
            db.session.commit()
            return render_template("pay.jinja", tenant=tenants, cart=carts, numMethods=len(trx.trx_methods), trx=trx)
        else:
            args = request.args
            carts.updated = datetime.now()
            carts.epan = args.get("epan")
            carts.lpn = args.get("lpn")
            carts.amount = args.get("amount")
            carts.currency = args.get("currency")
            carts.authorizeTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.session.commit()
            return render_template("cart.jinja", tenant=tenants, cart=carts)

    else:
        if carts.pgs_id.payStatus == 2:
            shc = carts.pgs_id.payShcId
            trx = get_pay_methods(tenants, carts, shc)
            return render_template("pay.jinja", tenant=tenants, cart=carts, numMethods=len(trx.trx_methods), trx=trx)
        else:
            if carts.pgs_id.payStatus == 0:
                url = url_for("viewCartId", uuid=carts.approve_uuid) + f"?epan={carts.epan}" + f"&amount={carts.pgs_id.payAmount}" + f"&currency={carts.pgs_id.payCurrency}" + f"&payId={carts.pgs_id.payId}"
            else:
                url = url_for("viewCartId", uuid=carts.decline_uuid) + f"?epan={carts.epan}" + f"&amount={carts.pgs_id.payAmount}" + f"&currency={carts.pgs_id.payCurrency}" + f"&payId={carts.pgs_id.payId}" + f"&payDescr={carts.pgs_id.payDescription}"

            return render_template("customer.jinja", tenant=tenants, cart=carts, qr=qrcode(f'{url}'), url=url)



@flask_app.route("/lpns/", methods=["POST"])
def viewLpn():
    tenants = Tenants.query.filter_by(id = 1).first()
    lpn = None
    carts = None
    if len(request.form['lpn']) > 0:
        lpn = request.form['lpn']
        carts = Carts.query.filter(func.upper(Carts.lpn) == func.upper(lpn)).first()

        if carts != None:
            if carts.pgs_id == None:
                lpn = carts.lpn
                return render_template("lpn.jinja", tenant=tenants, cart=carts, lpn=lpn)
            else:
                if carts.pgs_id.payStatus == 0:
                    url = url_for("viewCartId", uuid=carts.approve_uuid)
                else:
                    url = url_for("viewCartId", uuid=carts.decline_uuid)
                return render_template("customer.jinja", tenant=tenants, cart=carts, qr=qrcode(f'{url}'), url=url)
        else:
            flash(f"LPN: {lpn} not found", "fail")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))



@flask_app.route("/lpns/<string:lpn>", methods=["GET"])
def viewLpnId(lpn):
    tenants = Tenants.query.filter_by(id = 1).first()
    carts = None
    if len(lpn) > 0:
        carts = Carts.query.filter(func.upper(Carts.lpn) == func.upper(lpn)).first()

        if carts != None:
            if carts.pgs_id == None:
                lpn = carts.lpn
                return render_template("lpn.jinja", tenant=tenants, cart=carts, lpn=lpn)
            else:
                if carts.pgs_id.payStatus == 0:
                    url = url_for("viewCartId", uuid=carts.approve_uuid)
                else:
                    url = url_for("viewCartId", uuid=carts.decline_uuid)
                return render_template("customer.jinja", tenant=tenants, cart=carts, qr=qrcode(f'{url}'), url=url)
        else:
            flash(f"LPN: {lpn} not found", "fail")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
