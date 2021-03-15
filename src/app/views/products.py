from flask import jsonify, request
from flask import Flask, render_template
# from .products_operations import search_products, add_products, USAdapter


## main endpoints file

from ..app import app


@app.route('/main', methods=['POST', 'GET'])
def mainPage():
    return {'Welcome to GelAl':200}

@app.route('/', methods=['POST', 'GET'])
def Nolink():
    return {'Not Found: Please use a valid endpoint': 400}