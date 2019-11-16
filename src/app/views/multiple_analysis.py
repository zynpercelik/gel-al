from flask import jsonify, request
from flask_jwt import jwt_required, current_identity
from sqlalchemy import and_
from sqlalchemy.types import Float
from ..utils import similarty_dict
from ..visualization import HeatmapVisualization
import time
from ..app import app
from ..schemas import *
from ..models import db, User, Analysis, MetabolomicsData, Method
from ..tasks import save_analysis
from ..base import *
from ..dpm import *
import datetime







@app.route('/excel', methods =['GET','POST'])
def excel():
    data = request.json['data']
    meta = request.json['meta']
    processed_data = excel_data_Prpcessing(data,meta)

    return jsonify(processed_data)

"""
this function takes data from excel sheet and return a list of metabolites in the sheet
"""
def metabolc(data):
    metabols = []
    for k in range(1, len(data), 1):
        if len(data[k]) > 0:
            metabols.append(data[k][0])
    return metabols


"""
    this function returns a list of users and their values for each metabolite ex: "user 1" : [0,0,0.33,1.2021,0,0] where each value represent a metabolite
    for every metabol in a certain user data
"""
def user_metabol(data):
    headline = data[0]
    users = []
    container = []
    user_metabolites = {}
    id ="-"

    for i in range(1, len(headline), 1):
        temp = []
        for j in data:
            if len(j) > 0:
                    temp.append(j[i])
        container.append(temp)

    for row in container:
        temp2 = []
        for value in range(1,len(row),1):
            id = row[0]
            temp2.append(row[value])

        user_metabolites[id] = temp2
    # for k,v in user_metabolites.items():
    #     print (k,v)
    return user_metabolites

"""
returns a dictionary for a study with its users info, metabolites and labels {studyname, control_label, analysis:{user:{metabolites,label}}}
"""
def excel_data_Prpcessing(data, meta):

    meta_data = meta_data_processing(meta)
    study_name = meta_data[0]
    group_control_label = meta_data[1]
    users_labels = meta_data[2]

    users_metabolite = {}
    data2 = user_metabol(data)
    metabol = metabolc(data)
    #
    for key, value in data2.items():
        temp = []
        for index_metas in range(0, len(value), 1):
            temp.append([metabol[index_metas], value[index_metas]])
        users_metabolite[key] = {"Metabolites": temp, "Label": users_labels[key]}

    processed_users_data = {"study_name": study_name, "control_label": group_control_label,
                            "analysis": users_metabolite}
    # for k,v in processed_users_data.items():
    #     print (k,v)
    return processed_users_data

"""
a function to extract study name, control label, and users labels
"""
def meta_data_processing(meta):
    users_labels = {}
    study_name = meta[0][1]
    group_control_label = meta[1][1]
    for i in range(3, len(meta), 1):
        if len(meta[i]) != 0:
            users_labels[meta[i][0]] = meta[i][1]

    return [study_name, group_control_label, users_labels]