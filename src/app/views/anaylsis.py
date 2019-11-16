from functools import reduce
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

@app.route('/analysis/fva', methods=['POST'])
@jwt_required()
def fva_analysis():
    """
    FVA analysis
    ---
    tags:
      - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
        - in: body
          name: body
          schema:
            id: AnalysisInput
            required:
              - name
              - concentration_changes
            properties:
              name:
                  type: string
                  description: name of analysis
              concentration_changes:
                  type: object
                  description: concentration changes of metabolitics
    responses:
      200:
        description: Analysis info
      404:
        description: Analysis not found
      401:
        description: Analysis is not yours
    """
    # (data, error) = AnalysisInputSchema().load(request.json)
    data = request.json
    # print (request.json)
    # if error:
    #     return jsonify(error), 400

    if not request.json:
        return "", 404
    changes = request.json['concentration_changes']

    user = User.query.get(2)
    metabolomics_data = MetabolomicsData(
        metabolomics_data = changes,
        owner_email = 'tajtest2019@gmail.com',
        is_public = True if request.json['public'] else False
    )
    db.session.add(metabolomics_data)
    db.session.commit()

    analysis = Analysis(name =request.json['name'], user = user)
    analysis.name = request.json['name']
    analysis.type = 'public' if request.json['public'] else 'private'
    analysis.start_time = datetime.datetime.now()

    analysis.owner_user_id = user.id
    analysis.owner_email = user.email
    analysis.method_id = 1
    analysis.metabolomics_data_id = metabolomics_data.id
    analysis.dataset_id = 0

    # print (analysis.method_id, analysis.metabolomics_data_id)

    db.session.add(analysis)
    db.session.commit()

    save_analysis.delay(analysis.id, data['concentration_changes'])
    return jsonify({'id': analysis.id})


    #
    # temp = "public" if data['public'] else "private"
    # analysis = Analysis(
    #     data['name'],
    #     current_identity,
    #     type= temp)
    # db.session.add(analysis)
    # db.session.commit()
    # analysis_id = analysis.id
    # # print (analysis_id)
    # save_analysis.delay(analysis_id, data['concentration_changes'])
    # return jsonify({'id': analysis_id})



@app.route('/analysis/set', methods=['POST'])
def user_analysis_set():
    """
    List of analysis of user
    ---
    tags:
        - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
    """
    data = request.json['data']
    analyses = Analysis.get_multiple(data.values())
    print (data,'------------------>1')
    #
    # if len(analyses) != len(request.args):
    #     return '', 401
    X = [i.results_pathway for i in analyses]
    y = [i.name for i in analyses]
    # print (analyses,'------------------>2')
    return AnalysisSchema(many=True).jsonify(analyses)


@app.route('/analysis/visualization', methods=['POST'])
def analysis_visualization():
    """
    List of analysis of user
    ---
    tags:
        - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
    """

    data = request.json['data']
    analyses = Analysis.get_multiple(data.values())
    #
    # if len(analyses) != len(request.args):
    #     return '', 401
    # X = [i.results_pathway for i in analyses]
    # y = [i.name for i in analyses]


    # analyses = list(Analysis.get_multiple(request.args.values()))
    # if len(analyses) != len(request.args):
    #     return '', 401
    X = [i.results_pathway[0] for i in analyses]

    y = [i.name for i in analyses]

    return jsonify(HeatmapVisualization(X, y).clustered_data())


# @app.route('/analysis/<type>')
# def disease_analysis(type: str):
#     """
#     List of disease analysis avaliable in db
#     ---
#     tags:
#         - analysis
#     parameters:
#         -
#           name: authorization
#           in: header
#           type: string
#           required: true
#     """
#     return AnalysisSchema(many=True).jsonify(
#         Analysis.query.filter_by(type=type).with_entities(
#             Analysis.id, Analysis.name, Analysis.status))

#
# @app.route('/analysis/detail/<id>')
# def analysis_detail1(id):
#     """
#     Get analysis detail from id
#     ---
#     tags:
#       - analysis
#     parameters:
#         -
#           name: authorization
#           in: header
#           type: string
#           required: true
#         -
#           name: id
#           in: path
#           type: integer
#           required: true
#     responses:
#       200:
#         description: Analysis info
#       404:
#         description: Analysis not found
#       401:
#         description: Analysis is not yours
#     """
    # analysis = Analysis.query.get(id)
    # if not analysis:
    #     return '', 404
    # if not analysis.authenticated():
    #     return '', 401
    # return AnalysisSchema().jsonify(analysis)

@app.route('/analysis/most-similar-diseases/<id>')
def most_similar_diseases(id: int):
    """
    Calculates most similar disease for given disease id
    ---
    tags:
      - analysis
    parameters:
      -
        name: authorization
        in: header
        type: string
        required: true
      -
        name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Most similar diseases
      404:
        description: Analysis not found
      401:
        description: Analysis is not yours
    """
    analysis = Analysis.query.get(id)
    if not analysis:
        return '', 404
    if not analysis.authenticated():
        return '', 401

    row_disease_analyses = Analysis.query.filter_by(
        type='disease').with_entities(Analysis.name,
                                      Analysis.results_pathway).all()

    names, disease_analyses = zip(*[(i[0], i[1][0])
                                    for i in row_disease_analyses])

    sims = similarty_dict(analysis.results_pathway[0], list(disease_analyses))
    top_5 = sorted(zip(names, sims), key=lambda x: x[1], reverse=True)[:5]

    return jsonify(dict(top_5))


@app.route('/analysis/list')
@jwt_required()
def user_analysis():
    """
    List of analysis of user
    ---
    tags:
        - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
    """
    return AnalysisSchema(many=True).jsonify(
        current_identity.analysis.filter_by(type='private').with_entities(
            Analysis.id, Analysis.name, Analysis.status))

@app.route('/analysis/search-by-change', methods=['POST'])
def search_analysis_by_change():
    """
    Search query in db
    ---
    tags:
        - analysis
    parameters:
        -
          name: query
          in: url
          type: string
          required: true
    """
    (data, error) = PathwayChangesScheme().load(request.json, many=True)
    if error:
        return jsonify(error), 400

    return AnalysisSchema(many=True).jsonify(
        Analysis.query.filter_by_change_many(data)
        .filter_by_change_amount_many(data).filter_by_authentication()
        .with_entities(Analysis.id, Analysis.name, Analysis.status))


############################################################# new parts

@app.route('/analysis/direct-pathway-mapping', methods=['GET', 'POST'])
def direct_pathway_mapping():
    if not request.json:
        return "", 404
    changes = request.json['concentration_changes']

    user = User.query.get(1)
    metabolomics_data = MetabolomicsData(
        metabolomics_data = changes,
        owner_email = 'alperdokay@std.sehir.edu.tr',
        is_public = True if request.json['public'] else False
    )
    db.session.add(metabolomics_data)
    db.session.commit()

    analysis = Analysis(name =request.json['name'], user = user)
    analysis.name = request.json['name']
    analysis.status = True
    analysis.type = 'public' if request.json['public'] else 'private'
    analysis.start_time = datetime.datetime.now()
    analysis.end_time = datetime.datetime.now()

    analysis.owner_user_id = user.id
    analysis.owner_email = user.email
    analysis.method_id = 2
    analysis.metabolomics_data_id = metabolomics_data.id
    analysis.dataset_id = 0

    print (analysis.method_id, analysis.metabolomics_data_id)
    analysis_runs = DirectPathwayMapping(changes)  # Forming the instance
    # fold_changes
    analysis_runs.run()  # Making the analysis
    analysis.results_pathway = [analysis_runs.result_pathways]
    analysis.results_reaction = [analysis_runs.result_reactions]

    db.session.add(analysis)
    db.session.commit()

    # analysis.owner_user_id = user.id
    # analysis.owner_email = user.email
    # analysis.method_id = 2
    # analysis.metabolomics_data_id = metabolomics_data.id
    # analysis.dataset_id = 0
    # analysis.start_time = datetime.datetime.now()
    # analysis.end_time = datetime.datetime.now()

    analysis_id = analysis.id
    return jsonify({'id': analysis.id})


@app.route('/analysis/detail/<id>')
def analysis_detail(id):
    analysis = Analysis.query.get(id)
    metabolomics_data = MetabolomicsData.query.get(analysis.metabolomics_data_id)
    method = Method.query.get(analysis.method_id)
    data = {
        'name': analysis.name,
        'status': analysis.status,
        'results_pathway': analysis.results_pathway,
        'results_reaction': analysis.results_reaction,
        'method': method.name,
        'fold_changes': metabolomics_data.metabolomics_data
    }
    # print(jsonify(data))
    return jsonify(data)

@app.route('/analysis/<type>')
def analysis_details(type):
    methods = Method.query.all()
    data = Analysis.query.filter_by(type=type).with_entities(
        Analysis.id, Analysis.name, Analysis.status, Analysis.method_id)
    returned_data = []
    for test in data:
        method = Method.query.filter_by(id=test[3]).first()

        print(method)
        returned_data.append({
            'id': test[0],
            'name': test[1],
            'status': test[2],
            'method': method.name
        })
        print(test)
    return jsonify(returned_data)

# @app.route('/analysis/set')
# def analysis_set():
# return ""