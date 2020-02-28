from flask import jsonify, request
from flask_jwt import jwt_required, current_identity
from sqlalchemy import and_
from sqlalchemy.types import Float
from flask import Flask, render_template

import time
from ..app import app

from ..models import db, Products, Customers, Transactions





@app.route('/searchdb-products', methods=['POST', 'GET'])
def searchDB_product():

    result = []
    keyword  = request.form['data'].strip()
    if len(keyword) == 0:
        keyword = '--empty--'
    products = Products()
    data = list(products.query.all())
    for prod in data:
        prod = str(prod).split(' <class')[0].split(",")
        # print(prod)
        if keyword in prod[0]:
            result.append([prod[0],prod[2],prod[1],prod[3]])
    return render_template('result_table.html',result=result)


@app.route('/adddb-products', methods=['POST', 'GET'])
def addDB_product():

    name  = request.form['product_name']
    cat = request.form["Product_category"]
    quant = request.form["quantity"]
    price = request.form["price"]

    print(name,cat,quant,price)

    products = Products()
    products.price = price
    products.name = name
    products.quantity = quant
    products.category = cat

    db.session.add(products)
    db.session.commit()

    return render_template('main.html')


@app.route('/main', methods=['POST', 'GET'])
def mainPage():
    dicte  = dict(request.form)
    if '1' in dicte:
        return render_template('main_switch.html')
    elif '2' in dicte:
        return render_template('main.html')
    else:
        return render_template('main.html')


@app.route('/add-customers', methods=['POST', 'GET'])
def add_customer():
    return render_template('add_customers.html')


@app.route('/add-products', methods=['POST', 'GET'])
def add_product():
    return render_template('add_products.html')


@app.route('/add-trans', methods=['POST', 'GET'])
def add_tran():
    return render_template('add_trans.html')


@app.route('/search-customers', methods=['POST', 'GET'])
def search_customer():
    return render_template('search_customers.html')


@app.route('/search-products', methods=['POST', 'GET'])
def search_product():
    return render_template('search_products.html')


@app.route('/search-trans', methods=['POST', 'GET'])
def search_tran():
    return render_template('search_trans.html')


