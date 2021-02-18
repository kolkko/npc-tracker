import os
import json

from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from jose import jwt

from models import setup_db, Npc, Place
from forms import *
from auth import *

AUTH0_DOMAIN = 'dev-test-fsnd.eu.auth0.com'
API_AUDIENCE = 'npc-tracker'
ALGORITHMS = ["RS256"]
AUTH0_LOGIN = 'https://dev-test-fsnd.eu.auth0.com/authorize?audience=npc-tracker&response_type=token&client_id=dvbXKtL4j4yu4JL3gQsWsws7BwFIlXPF&redirect_uri=http://127.0.0.1:5000/index'

bearer_tokens = {
  "Dungeon Master": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImpoSWFSYWdqMUxtU0pEazZESTJDdiJ9.eyJpc3MiOiJodHRwczovL2Rldi10ZXN0LWZzbmQuZXUuYXV0aDAuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTAyNzM1NDM5MDU1NTU5MTYyMTE5IiwiYXVkIjpbIm5wYy10cmFja2VyIiwiaHR0cHM6Ly9kZXYtdGVzdC1mc25kLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MTM1NTI2MjksImV4cCI6MTYxMzU1OTgyOSwiYXpwIjoiZHZiWEt0TDRqNHl1NEpMM2dRc1dzd3M3QndGSWxYUEYiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiYWRkOm5wYyIsImRlbGV0ZTpucGMiLCJlZGl0Om5wYyIsImdldDpucGNzIl19.Bk4H9-CUJlSkp9jZj4OZXebGdOjy7bMxNtJi6gvTyLDn4HJ7OXiJRHywVRllCpnhHSWSL1bTG2W6S1HEL236uPKRHjku98tbJFNwQW_quFUuDHhpxf7gWl-rD0-PNVx7mAblgvDc_qWvJsa1CDuNLR3Ht4Vs1lNaCS5vXSDnU21IgWll-2joWUYtklv67k5AwrjFQJwih1irahgEIn-TpTNMQP5reyHDpMQ1FtnyDOhlGYq6WR_m7LOcE-As3JTOfTtNFH5rhUYld4vJm6BmI13JCm_g1dLMafNt_dpEAOCF8-ea0hsbCYf2HUAAz5i3IItl9VoFSM624tu49Hgnhw",
  "": ""
}

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  app.config['SECRET_KEY'] = os.urandom(32)
  CORS(app)

  # -----------------------------------------------------------
  # Login and home
  # -----------------------------------------------------------

  @app.route('/')
  def login():
    return render_template('login.html'), 200

  @app.route('/index')
  @requires_auth('get:npcs')
  def index():
    return render_template('index.html', data=Npc.query.all()), 200

  # -----------------------------------------------------------
  # CRUD Operations for NPCs # TODO: PATCH, DELETE
  # -----------------------------------------------------------

  @app.route('/npcs', methods=['GET'])
  def get_npcs():
    results = Npc.query.order_by(Npc.id).all()
    npcs = [npc.format() for npc in results]
    return jsonify({
      'success' : True,
      'npcs' : npcs
    })

  @app.route('/npcs/<int:npc_id>', methods=['GET'])
  def get_one_npc(npc_id):
    selection = Npc.query.filter(
            Npc.id == npc_id).one_or_none()
    if not selection:
        abort(400)
    npc = selection.format()
    return render_template('npc.html', data=npc), 200

  @app.route('/npcs/create', methods=['POST'])
  def post_npc():
    form = NpcForm(request.form)
    if not form:
      abort(400)
    try:
      new_npc = Npc(
        name=request.form['name'],
        appearance=request.form['appearance'],
        occupation=request.form['occupation'],
        roleplaying=request.form['roleplaying'],
        background=request.form['background'], 
        place_id=request.form['place_id']
      )
      new_npc.insert()
      selection = Npc.query.order_by(Npc.id).all()
      return render_template('index.html', data=selection)
    except Exception:
      abort(422)

  
  @app.route('/npcs/<int:npc_id>', methods=['DELETE'])
  def delete_npc(npc_id):
    print('about to delete')
    selection = Npc.query.filter(
        Npc.id == npc_id).one_or_none()
    print("selection")
    if not selection:
        abort(400)
    try:
        selection.delete()
        print('deleted', npc_id)
        return jsonify({
          'success': True,
          'deleted': npc_id
          })
    except Exception:
        abort(422)

  # -----------------------------------------------------------
  # CRUD Operations for Location TODO
  # -----------------------------------------------------------

  @app.route('/places', methods=['GET'])
  def get_places():
    results = Place.query.order_by(Place.id).all()
    places = [place.format() for place in results]
    return render_template('places.html', data=places)

  @app.route('/places/<int:place_id>', methods=['GET'])
  def get_one_place():
    selection = Place.query.filter(
            Place.id == place_id).one_or_none()
    if not selection:
        abort(400)
    place = selection.format()
    return jsonify({
      'success' : True,
      'place' : place
    })

  @app.route('/places/create', methods=['POST'])
  def post_place():
    print("posting new place")
    # # form = PlaceForm(request.form)
    # print("Form name: ", request.form['name'])
    # print("Form name: ", request.form['location'])
    # print("Form name: ", request.form['description'])
    # if not form:
    #   abort(400)
    try:
      print('create new place')
      new_place = Place(
        new_name=request.form['name'],
        new_location=request.form['location'],
        new_description=request.form['description']
      )
      print('about to insert data')
      new_place.insert()
      print('data has been inserted')
      selection = Place.query.order_by(Place.id).all()
      return render_template('places.html', data=selection)
    except Exception:
      abort(422)

  
  @app.route('/places/<int:place_id>', methods=['DELETE'])
  def delete_place(place_id):
    print('about to delete')
    selection = Place.query.filter(
        Place.id == place_id).one_or_none()
    print("selection")
    if not selection:
        abort(400)
    try:
        selection.delete()
        print('deleted', place_id)
        return jsonify({
          'success': True,
          'deleted': place_id
          })
    except Exception:
        abort(422)


  # -----------------------------------------------------------
  # Create resources
  # -----------------------------------------------------------
  @app.route('/npcs/create', methods=['GET'])
  def create_npc_form():
    form = NpcForm()
    return render_template('new_npc.html', form=form)

  @app.route('/places/create', methods=['GET'])
  def create_place_form():
    form = PlaceForm()
    return render_template('new_place.html', form=form)

  # ----------------------------------------------------------------------------
  # API error handlers
  # ----------------------------------------------------------------------------

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable entity'
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
    }), 422

  return app

app = create_app()
if __name__ == '__main__':
  APP.run(debug=True)