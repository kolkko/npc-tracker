import os
from flask import Flask, request, abort, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from models import setup_db, Npc, Place
from forms import *





def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  app.config['SECRET_KEY'] = os.urandom(32)
  # CORS(app)

  @app.route('/')
  def index():
    return render_template('index.html', data=Npc.query.all())

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
  def get_one_npc():
    selection = Npc.query.filter(
            Npc.id == npc_id).one_or_none()
    if not selection:
        abort(400)
    npc = selection.format()
    return jsonify({
      'success' : True,
      'npc' : npc
    })

  @app.route('/npcs/create', methods=['POST'])
  def post_npc():
    print("posting new npc")
    form = NpcForm(request.form)
    print("Form name: ", request.form['name'])
    if not form:
      abort(400)
    try:
      print('create new npc')
      new_npc = Npc(
        name=request.form['name'],
        appearance=request.form['appearance'],
        occupation=request.form['occupation'],
        roleplaying=request.form['roleplaying'],
        background=request.form['background'], 
        place_id=request.form['place_id']
      )
      print('about to insert data')
      new_npc.insert()
      print('data has been inserted')
      selection = Npc.query.order_by(Npc.id).all()
      return jsonify({
        'success': True,
        'npc_id': new_npc.id,
      })
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


  # -----------------------------------------------------------
  # Create resources
  # -----------------------------------------------------------
  @app.route('/npcs/create', methods=['GET'])
  def create_npc_form():
    form = NpcForm()
    return render_template('new_npc.html', form=form)

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