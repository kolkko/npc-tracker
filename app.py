# ----------------------------------------------------------------------------#
# Imports and Auth0
# ----------------------------------------------------------------------------#
import os
import requests
from flask import (Flask, request, abort, jsonify, render_template,
                   session, flash, make_response, Response, url_for, redirect)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from models import setup_db, Place, Npc
import simplejson as json
from auth import requires_auth, AuthError
from forms import NpcForm, PlaceForm
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

AUTH0_CALLBACK_URL = os.getenv('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_BASE_URL = os.getenv('AUTH0_BASE_URL')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')


# ----------------------------------------------------------------------------#
# Create and configure the application
# ----------------------------------------------------------------------------#
def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    setup_db(app)
    CORS(app)

    # -------------------------------------------------------------------------#
    # Auth0 and login
    # -------------------------------------------------------------------------#

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_BASE_URL,
        access_token_url='https://dev-test-fsnd.eu.auth0.com' + '/oauth/token',
        authorize_url='https://dev-test-fsnd.eu.auth0.com' + '/authorize',
        client_kwargs={'scope': 'openid profile email'}
      )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # route handler for home page when anonymous user visits
    @app.route('/')
    @cross_origin()
    def index():
        return render_template('login.html')

    @app.route('/about')
    @cross_origin()
    def about():
        return render_template('about.html')

    # route handler to log in
    @app.route('/login', methods=['GET'])
    @cross_origin()
    def login():
        print('Audience: {}'.format(AUTH0_AUDIENCE))
        return auth0.authorize_redirect(
          redirect_uri='%s/callback' % AUTH0_CALLBACK_URL,
          audience=AUTH0_AUDIENCE
          )

    # route handler for home page once logged in
    @app.route('/callback', methods=['GET'])
    @cross_origin()
    def post_login():
        token = auth0.authorize_access_token()
        session['token'] = token['access_token']
        print(session['token'])
        return redirect(url_for('npcs'))

    @app.route('/logged-in')
    @cross_origin()
    @requires_auth('get:npcs')
    def logged_in(payload):
        return render_template('logged-in.html')

    # route handler to log out
    @app.route('/logout')
    def log_out():
        # clear the session
        session.clear()
        # redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True),
                  'client_id': AUTH0_CLIENT_ID}
        return redirect('https://dev-test-fsnd.eu.auth0.com' +
                        '/v2/logout?' + urlencode(params))

    # -------------------------------------------------------------------------#
    # CRUD Operations for Npc
    # -------------------------------------------------------------------------#

    @app.route('/npcs', methods=['GET'])
    @cross_origin()
    @requires_auth('get:npcs')
    def npcs(payload):
        data = Npc.query.filter(
            Npc.user_id == payload['sub']).all()
        places = Place.query.all()
        place_names = []
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

    @app.route('/npcs/<int:npc_id>', methods=['GET'])
    @cross_origin()
    @requires_auth('get:npcs')
    def get_one_npc(payload, npc_id):
        selection = Npc.query.filter(
                Npc.id == npc_id).one_or_none()
        if not selection:
            abort(400)
        if selection.user_id != payload['sub']:
            abort(401)
        npc = selection.format()
        return render_template('npc.html', data=npc), 200

    @app.route('/npcs/create', methods=['POST'])
    @cross_origin()
    @requires_auth('add:npc')
    def post_npc(payload):
        form = NpcForm(request.form)
        if not form:
            abort(400)
        npc_place = Place.query.filter(
                Place.id == request.form['place_id']).one_or_none()
        try:
            new_npc = Npc(
                name=request.form['name'],
                appearance=request.form['appearance'],
                occupation=request.form['occupation'],
                roleplaying=request.form['roleplaying'],
                background=request.form['background'],
                place_id=npc_place.id,
                user_id=payload['sub']
            )
            new_npc.insert()
            return redirect(url_for('npcs'))
        except Exception:
            abort(422)

    @app.route('/npcs/<int:npc_id>/edit', methods=['POST'])
    @cross_origin()
    @requires_auth('edit:npc')
    def update_npc(payload, npc_id):
        form = NpcForm(request.form)
        npc = Npc.query.filter(
            Npc.id == npc_id).one_or_none()
        if not form:
            abort(400)
        npc_place = Place.query.filter(
                Place.id == request.form['place_id']).one_or_none()
        try:
            npc.name = request.form['name'],
            npc.appearance = request.form['appearance'],
            npc.occupation = request.form['occupation'],
            npc.roleplaying = request.form['roleplaying'],
            npc.background = request.form['background'],
            npc.place_id = npc_place.id
            npc.update()
            return redirect(url_for('npcs'))
        except Exception:
            abort(422)

    @app.route('/npcs/<int:npc_id>/delete', methods=['GET'])
    @cross_origin()
    @requires_auth('delete:npc')
    def delete_npc(payload, npc_id):
        print('about to delete')
        selection = Npc.query.filter(
          Npc.id == npc_id).one_or_none()
        if not selection:
            abort(400)
        if selection.user_id != payload['sub']:
            abort(401)
        try:
            selection.delete()
            return redirect(url_for('npcs'))
        except Exception:
            abort(422)

    # -------------------------------------------------------------------------#
    # CRUD Operations for Place
    # -------------------------------------------------------------------------#

    @app.route('/places', methods=['GET'])
    @cross_origin()
    @requires_auth('get:npcs')
    def get_places(payload):
        results = Place.query.order_by(Place.location).all()
        places = [place.format() for place in results]
        return render_template('places.html', data=places), 200

    @app.route('/places/<int:place_id>', methods=['GET'])
    @cross_origin()
    @requires_auth('get:npcs')
    def get_one_place(payload, place_id):
        selection = Place.query.filter(
                Place.id == place_id).one_or_none()
        if not selection:
            abort(400)
        place = selection.format()
        return render_template('place.html', data=place), 200

    @app.route('/places/create', methods=['POST'])
    @cross_origin()
    @requires_auth('add:npc')
    def post_place(payload):
        try:
            new_place = Place(
                name=request.form['name'],
                location=request.form['location'],
                description=request.form['description'],
                user_id=payload['sub']
            )
            print('about to insert data')
            new_place.insert()
            print('data has been inserted')
            return redirect(url_for('get_places'))
        except Exception:
            abort(422)

    @app.route('/places/<int:place_id>/edit', methods=['POST'])
    @cross_origin()
    @requires_auth('edit:npc')
    def update_place(payload, place_id):
        form = PlaceForm(request.form)
        place = Place.query.filter(
            Place.id == place_id).one_or_none()
        if not form:
            abort(400)
        try:
            place.name = request.form['name'],
            place.location = request.form['location'],
            place.description = request.form['description'],
            place.update()
            return redirect(url_for('get_places'))
        except Exception:
            abort(422)

    @app.route('/places/<int:place_id>/delete', methods=['GET'])
    @cross_origin()
    @requires_auth('delete:npc')
    def delete_place(payload, place_id):
        linked_npcs = Npc.query.filter(
            Npc.place_id == place_id).all()
        if linked_npcs:
            abort(400)
        selection = Place.query.filter(
            Place.id == place_id).one_or_none()
        print("selection")
        if not selection:
            abort(400)
        try:
            selection.delete()
            return redirect(url_for('get_places'))
        except Exception:
            abort(422)

    # -------------------------------------------------------------------------#
    # View places associated with a location
    # -------------------------------------------------------------------------#

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

    # -------------------------------------------------------------------------#
    # Create resources
    # -------------------------------------------------------------------------#

    @app.route('/npcs/create', methods=['GET'])
    @cross_origin()
    @requires_auth('add:npc')
    def create_npc_form(payload):
        form = NpcForm()
        data = Place.query.order_by(Place.location).all()
        places_list = [(d.id, d.name) for d in data]
        form.place_id.choices = places_list
        return render_template('new_npc.html', form=form)

    @app.route('/npcs/<int:npc_id>/edit', methods=['GET'])
    @cross_origin()
    @requires_auth('edit:npc')
    def edit_npc(payload, npc_id):
        selection = Npc.query.filter(
            Npc.id == npc_id).one_or_none()
        if not selection:
            abort(400)
        current_place = Place.query.filter(
            Place.id == selection.place_id).one_or_none()
        data = Place.query.order_by(Place.location).all()
        places_list = [(current_place.id, current_place.name)]
        for d in data:
            places_list.append((d.id, d.name))
        print(places_list)
        form = NpcForm()
        form.name.data = selection.name
        form.appearance.data = selection.appearance
        form.occupation.data = selection.occupation
        form.roleplaying.data = selection.roleplaying
        form.background.data = selection.background
        form.place_id.choices = places_list
        return render_template('edit_npc.html', form=form,  data=selection)

    @app.route('/places/create', methods=['GET'])
    @cross_origin()
    @requires_auth('add:npc')
    def create_place_form(payload):
        form = PlaceForm()
        return render_template('new_place.html', form=form)

    @app.route('/places/<int:place_id>/edit', methods=['GET'])
    @cross_origin()
    @requires_auth('add:npc')
    def edit_place(payload, place_id):
        selection = Place.query.filter(
            Place.id == place_id).one_or_none()
        if not selection:
            abort(400)
        form = PlaceForm()
        form.name.data = selection.name
        form.location.data = selection.location
        form.description.data = selection.description
        return render_template('edit_place.html', form=form,  data=selection)

    # -------------------------------------------------------------------------#
    # API error handlers
    # -------------------------------------------------------------------------#

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': 401,
            "message": "unauthorized"
        }), 401

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
# Launch app
if __name__ == '__main__':
    APP.run(debug=True)
