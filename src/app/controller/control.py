from flask import jsonify, request
from flask import Flask, render_template
from .products_operations import search_products, add_products

from ..app import app

from ..models import db, Products, Customers, Transactions





@app.route('/searchdb-products', methods=['POST', 'GET'])
def searchDB_product():

    keyword  = request.form['data'].strip()
    if len(keyword) == 0:
        keyword = '--empty--'
    result = search_products(keyword).result

    return render_template('result_table.html',result=result)


@app.route('/adddb-products', methods=['POST', 'GET'])
def addDB_product():

    data = dict(request.form)
    result = search_products(data['product_name'][0]).result
    if len(result) == 0:
        add_products(data)

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


