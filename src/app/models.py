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
    email = db.Column(db.String(255))


    def __repr__(self):
        return (self.name,self.email,self.id)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    category = db.Column(db.String(255))

    def __repr__(self):
        return '{},{} ,{} ,{}'.format(self.name, self.price, self.quantity,self.category)


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(255))
    products = db.Column(JSON) #// should be json {product_id:quantity}
    date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return self.email
