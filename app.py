import os
import json

from flask import Flask, request, abort, jsonify, render_template, flash, redirect, url_for
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
  # Load Pages
  # -----------------------------------------------------------

  @app.route('/')
  def login():
    return render_template('login.html'), 200

  @app.route('/index')
  # @requires_auth('get:npcs')
  def index():
    data = Npc.query.all()
    places = Place.query.all()
    place_names= []
    for d in data:
      place_name = Place.query.filter(
            Place.id == d.place_id).one_or_none()
      place_names.append({
        'id': d.id,
        'name': d.name,
        'appearance': d.appearance,
        'occupation': d.occupation,
        'roleplaying': d.roleplaying,
        'background': d.background,
        'place_name': place_name.name
        })
    return render_template('index.html', data=place_names), 200



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
      return redirect(url_for('index'))
    except Exception:
      abort(422)

  @app.route('/npcs/<int:npc_id>/edit', methods=['POST'])
  def update_npc(npc_id):
    form = NpcForm(request.form)
    npc = Npc.query.filter(
        Npc.id == npc_id).one_or_none()
    if not form:
      abort(400)
    try:
      npc.name=request.form['name'],
      npc.appearance=request.form['appearance'],
      npc.occupation=request.form['occupation'],
      npc.roleplaying=request.form['roleplaying'],
      npc.background=request.form['background'], 
      npc.place_id=request.form['place_id']
      npc.update()
      return redirect(url_for('index'))
    except Exception:
      abort(422)



  @app.route('/npcs/<int:npc_id>/delete', methods=['GET'])
  def delete_npc(npc_id):
    print('about to delete')
    selection = Npc.query.filter(
      Npc.id == npc_id).one_or_none()
    if not selection:
      abort(400)
    try:
      selection.delete()
      return redirect(url_for('index'))
    except Exception:
      abort(422)

  # -----------------------------------------------------------
  # CRUD Operations for Place
  # -----------------------------------------------------------

  @app.route('/places', methods=['GET'])
  def get_places():
    results = Place.query.order_by(Place.location).all()
    places = [place.format() for place in results]
    return render_template('places.html', data=places), 200

  @app.route('/places/<int:place_id>', methods=['GET'])
  def get_one_place():
    selection = Place.query.filter(
            Place.id == place_id).one_or_none()
    if not selection:
        abort(400)
    place = selection.format()
    return redirect(url_for('places'))

  @app.route('/places/create', methods=['POST'])
  def post_place():
    try:
      new_place = Place(
        new_name=request.form['name'],
        new_location=request.form['location'],
        new_description=request.form['description']
      )
      print('about to insert data')
      new_place.insert()
      print('data has been inserted')
      selection = Place.query.order_by(Place.id).all()
      return redirect(url_for('places'))
    except Exception:
      abort(422)

  @app.route('/places/<int:place_id>/edit', methods=['POST'])
  def update_place(place_id):
    form = PlaceForm(request.form)
    place = Place.query.filter(
        Place.id == place_id).one_or_none()
    if not form:
      abort(400)
    try:
      place.name=request.form['name'],
      place.location=request.form['location'],
      place.description=request.form['description'],

      place.update()
      selection = Place.query.order_by(Place.id).all()
      return redirect(url_for('places'))
    except Exception:
      abort(422)

  @app.route('/places/<int:place_id>', methods=['GET'])
  def delete_place(place_id):
    selection = Place.query.filter(
        Place.id == place_id).one_or_none()
    print("selection")
    if not selection:
        abort(400)
    try:
        selection.delete()
        return redirect(url_for('places'))
    except Exception:
        abort(422)

  # -----------------------------------------------------------
  # View places associated with a location
  # -----------------------------------------------------------

  # @app.route('/locations')
  # # @requires_auth('get:npcs')
  # def locations():
  #   data = Npc.query.all()
  #   places = Place.query.all()
  #   place_names= []
  #   for d in data:
  #     place_name = Place.query.filter(
  #           Place.id == d.place_id).one_or_none()
  #     place_names.append({
  #       'id': d.id,
  #       'name': d.name,
  #       'appearance': d.appearance,
  #       'occupation': d.occupation,
  #       'roleplaying': d.roleplaying,
  #       'background': d.background,
  #       'place_name': place_name.name
  #       })
  #   return render_template('index.html', data=place_names), 200


  # -----------------------------------------------------------
  # Create resources
  # -----------------------------------------------------------
  @app.route('/npcs/create', methods=['GET'])
  def create_npc_form():
    form = NpcForm()
    return render_template('new_npc.html', form=form)

  @app.route('/npcs/<int:npc_id>/edit', methods=['GET'])
  def edit_npc(npc_id):
    selection = Npc.query.filter(
        Npc.id == npc_id).one_or_none()
    if not selection:
        abort(400)
    form = NpcForm()
    form.name.data = selection.name
    form.appearance.data = selection.appearance
    form.occupation.data = selection.occupation
    form.roleplaying.data = selection.roleplaying
    form.background.data = selection.background
    form.place_id.data = selection.place_id
    return render_template('edit_npc.html', form=form,  data=selection)    

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