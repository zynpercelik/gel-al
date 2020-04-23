from flask import jsonify, request
from sqlalchemy import and_
from sqlalchemy.types import Float
from flask import Flask, render_template

import time
from ..app import app
from ..models import db, Products


class search_products:
    """
    class to search products in DB, input: keyword of a product , output: list of matched products
    1 - checks current products in DB.
    2 - search by a keyword for a product .
    """
    def __init__(self,prodcut_name,rate):
        self.product_name = prodcut_name
        self.rate = rate
        self.data = self.get_DB_data()
        self.result = self.check_products()

    def get_DB_data(self):
        products = Products()
        data = list(products.query.all())

        return data

    def check_products(self):
        result = []

        for prod in self.data:
            prod = str(prod).split(' <class')[0].split(",")
            if self.product_name in prod[0]:
                product_liste = list(map(lambda x: prod[x] , range(4)))
                print(product_liste)
                product_liste[1] = str(int(product_liste[1].strip()) / self.rate)[:3]
                result.append(product_liste)

        return result



class add_products:
    """
    class to add products to DB, if the product exist in DB it wont be directed here since its handled in the controller
    input: a dictionary
    output: None

    """
    def __init__(self,product_details):

        self.product_details = product_details
        self.products = Products()
        self.index = len(list(map(lambda x: x , range(0))))

        self.add_product_session()

    def add_product_session(self):

        self.products.price = self.product_details['price'][self.index]
        self.products.name = self.product_details['product_name'][self.index]
        self.products.quantity = self.product_details['quantity'][self.index]
        self.products.category = self.product_details['Product_category'][self.index]

        db.session.add(self.products)
        db.session.commit()









class Currency(object):
    rate = 1

class EUEuro(Currency):
    rate = 7.5

class USDollar(Currency):
    rate = 7.0


class USAdapter(object):
    rate = USDollar.rate
    def __init__(self,keyword,rate = rate):
        self.keyword = keyword
        self.rate = rate

    def search_prod(self):
        data = search_products(self.keyword,self.rate).result
        return data




class EUAdapter(object):
    rate = EUEuro.rate
    def __init__(self,keyword,rate = rate):
        self.keyword = keyword
        self.rate = rate

    def search_prod(self):
        data = search_products(self.keyword,self.rate).result
        return data
