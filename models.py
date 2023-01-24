from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Tenant(TimestampMixin, db.Model):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = db.Column(db.Integer, primary_key=True)
    tenantName = db.Column(db.String(30), nullable=False)
    tenantCompany = db.Column(db.String(30))
    tenantStreet = db.Column(db.String(50))
    tenantCity = db.Column(db.String(30))
    tenantZip = db.Column(db.String(10))
    tenantCountry = db.Column(db.String(30))
    schemaName = db.Column(db.String(40), nullable=False)
    production = db.Column(db.Integer,nullable=False)
    suspend = db.Column(db.Integer,nullable=False)
