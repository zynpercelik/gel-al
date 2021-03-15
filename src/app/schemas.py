from marshmallow import Schema, fields
from flask_marshmallow import Marshmallow

from .app import app

ma = Marshmallow(app)

#
class LoginSchema(Schema):

    username = fields.String(required=True)
    phonenumber = fields.Integer(required=True)
    password = fields.String(required=True)



