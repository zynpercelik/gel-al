from flask import jsonify, request
from flask import Flask, render_template

from ..app import app




@app.route('/signup', methods=['POST', 'GET'])
def Signup():

    return {'Not Ready':200}


