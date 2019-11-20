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
import mwtab
from timeit import default_timer as timer





############################### Excel codes below

@app.route('/excel', methods =['GET','POST'])
def excel():
    data = request.json['data']
    meta = request.json['meta']
    processed_data = excel_data_Prpcessing(data,meta)

    return jsonify(processed_data)


def metabolc(data):
    """
    this function takes data from excel sheet and return a list of metabolites in the sheet
    """
    metabols = []
    for k in range(1, len(data), 1):
        if len(data[k]) > 0:
            metabols.append(data[k][0])
    return metabols



def user_metabol(data):

    """
        this function returns a list of users and their values for each metabolite ex: "user 1" : [0,0,0.33,1.2021,0,0] where each value represent a metabolite
        for every metabol in a certain user data
    """
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


def excel_data_Prpcessing(data, meta):

    """
    returns a dictionary for a study with its users info, metabolites and labels {studyname, control_label, analysis:{user:{metabolites,label}}}
    """

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


def meta_data_processing(meta):

    """
    a function to extract study name, control label, and users labels
    """
    users_labels = {}
    study_name = meta[0][1]
    group_control_label = meta[1][1]
    for i in range(3, len(meta), 1):
        if len(meta[i]) != 0:
            users_labels[meta[i][0]] = meta[i][1]

    return [study_name, group_control_label, users_labels]



################################################### MWtab codes below

def mwtabReader(name):

    dicte = {}
    liste = []
    subjects_samples = 0
    value_filter = [0,"0","N",""," "]
    mwfile = next(mwtab.read_files(name[0],name[1]))
    study_title = mwfile["PROJECT"]["PROJECT_TITLE"]
    measurment = mwfile["MS_METABOLITE_DATA"]["MS_METABOLITE_DATA_START"]["DATA"]

    for i in range(0,len(measurment),1):

        for j2 in measurment[i].keys(): ## dictionary of subjects
            if j2 != "metabolite_name":
                dicte.setdefault(j2,{})

        for j in measurment[i].keys():
            if j == "metabolite_name":  # measurement = {metabolite_name:name,....}
                metabol_name = measurment[i][j]  ## it will always have a value since measurement first key is metabolite_name ..
                liste.append(measurment[i][j])  ## list of metabolites
            else:
                for subject in dicte.keys():  #[subject_name]
                    if  measurment[i][subject] not in value_filter :
                        dicte[subject][metabol_name] =  measurment[i][subject]
                    # else:
                        # dicte[subject][metabol_name] = "0.0"
    return [dicte,study_title]




def checkDatabases(name):  # check if our used databases are used.
    mw = next(mwtab.read_files(name[0],name[1]))
    database = []
    data = mw["METABOLITES"]["METABOLITES_START"]["DATA"]
    keywords = ['kegg_id','pubchem_id','hmdb_id']
    for i in data[0].keys():
        if i in keywords:
            database.append(i)
    return database
def databaseProccesing(name):

    """
    checks if we have any of our databases
    checks which database has more metabolites available
    checks which database has more metabolites available
    # if everything is ok it returns the name and data of database
    """
    temp = checkDatabases(name)
    mapped = {}
    mapped_final = {}
    n = "" # temp name
    l = [] # temp len
    value_filter = [0,"0","N",""," "]
    if len(temp) > 0:  ## checks if we have any of our databases
        mw = next(mwtab.read_files(name[0],name[1]))
        data = mw["METABOLITES"]["METABOLITES_START"]["DATA"]
        for i in temp:  ## i is database name
            mapped.setdefault(i, {})
            for j in range(0,len(data),1):  ## j is index of ordered dict from mwtab file
                if data[j][i] not in value_filter:
                    mapped[i][data[j]["metabolite_name"]] = data[j][i]
        n = temp[0]
        l = mapped[n]
        for k,v in mapped.items():   ## checks which database has more metabolites available
            if len(v) > len(l) :
                l = v ; n = k
        if len(l) == 0:  ## checks which database has more metabolites available
            return 0
        else:
            mapped_final[n] = l   # if everything is ok it returns the name and data of database
            return  mapped_final
    else:
        return 0


@app.route('/workbench', methods =['GET','POST'])
def mwlab_mapper():

    """
    ## check 1 : if we have any database that we use
    ## if it passes check 1 we start mapping metabolite names to the database id.
    ## note that it can represent multiple samples
    """

    temp_name = request.json['data'].split()
    # print (name.split())
    std_id = temp_name[2].split(":")[1][2:]
    analysis_id = temp_name[3].split(":")[1][2:]
    print (std_id,analysis_id)
    name = [std_id,analysis_id]

    mapped = {}
    mapping_metabolites = {}
    mapping_data = databaseProccesing(name)  ## dictionary or 0
    if mapping_data != 0:
        data = open("../datasets/assets/mapping_all.txt","r+").readlines()
        for line in data:
            tempo = line.split(",")
            mapping_metabolites[tempo[0]]=tempo[1]

        local = mwtabReader(name)
        measurments_data= local[0]
        study_name = local[1]
        temp = list(mapping_data.keys())[0] # name of the database
        for sample,metabols_data in measurments_data.items():
            mapped.setdefault(sample, {})
            liste = []
            for metabol_name2,id in mapping_data[temp].items():
                for metabol_name1 , measurment in metabols_data.items():
                    if metabol_name1 == metabol_name2 and id in mapping_metabolites.keys():
                        liste.append([mapping_metabolites[id].strip(),float(measurment)])
            mapped[sample] = {"Metabolites": liste, "Label": "None"}
        return ({"study_name":study_name,"analysis":mapped,"group":"None"})
    else:
        return ({1:"Error"})



