from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Tenants(TimestampMixin, db.Model):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    company = db.Column(db.String(50))
    street = db.Column(db.String(50))
    city = db.Column(db.String(30))
    zip = db.Column(db.String(10))
    country = db.Column(db.String(30))
    schema = db.Column(db.String(40), nullable=False)
    production = db.Column(db.Integer,nullable=False)
    suspend = db.Column(db.Integer,nullable=False)

class Carts(TimestampMixin, db.Model):
    __tablename__ = "carts"
    __table_args__ = {"schema": "public"}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approve_uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decline_uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    epan = db.Column(db.String(30))
    lpn = db.Column(db.String(10))
    amount = db.Column(db.Integer)
    currency = db.Column(db.String(3))
    entryTime = db.Column(db.DateTime)
    authorizeTime = db.Column(db.DateTime)
    exitTime = db.Column(db.DateTime)

    def getFormattedAmount(self, amount):
        return '{},{:0<2}'.format(int(amount/100), int(amount%100))
