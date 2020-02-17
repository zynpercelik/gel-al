import uuid
import datetime
import json

from sqlalchemy import and_, or_
from sqlalchemy.types import Float
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy, BaseQuery
# from flask_jwt import jwt_required, current_identity, _jwt_required

from .app import app

db = SQLAlchemy(app)


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    affiliation = db.Column(db.String(255))
    password = db.Column(db.String(255))  # TODO: hash password
    analysis = db.relationship(
        "Analysis", back_populates="user", lazy='dynamic')

    def __repr__(self):
        return self.email
