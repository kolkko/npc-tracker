import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

from app import create_app
from models import setup_db, Npc, Place
from forms import *
from auth import requires_auth, AuthError
from config import Authtokens


class NpcTrackerTestCase(unittest.TestCase):

    # runs before each test
    def setUp(self):
        DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')
        DB_NAME = os.getenv('DB_NAME', 'npc_test')
        DB_PATH = ('postgresql+psycopg2://{}:{}@{}/{}'.
                   format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME))

        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.game_master = Authtokens["game_master"]
        self.viewer = Authtokens["viewer"]
        self.database_name = DB_NAME
        self.database_path = DB_PATH
        setup_db(self.app, self.database_path)

    # runs after each test
    def tearDown(self):
        print("tearDown")
        pass

    # -------------------------------------------------------------------------#
    # Test: Home
    # -------------------------------------------------------------------------#

    def test_home(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

    def test_home_error(self):
        res = self.client().get('/wrong')
        self.assertEqual(res.status_code, 404)

    def test_logged_in(self):
        res = self.client().get('/logged-in', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_logged_in_error(self):
        res = self.client().get('/logged-in', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    # -------------------------------------------------------------------------#
    # Test: RBAC
    # -------------------------------------------------------------------------#

    def test_rbac_success(self):
        res = self.client().get('/npcs/create', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_rbac_error(self):
        res = self.client().post('/npcs/create', headers={'Authorization':
                                 str(self.viewer), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    # -------------------------------------------------------------------------#
    # Test: NPC operations
    # -------------------------------------------------------------------------#

    def test_get_npcs(self):
        res = self.client().get('/npcs', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_get_npcs_error(self):
        res = self.client().get('/npcs', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_get_one_npc(self):
        res = self.client().get('/npcs/1', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_get_one_npc_error(self):
        res = self.client().get('/npcs/999999999', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_create_npc(self):
        with self.app.test_request_context(
            '/npcs/create', headers={'Authorization':
                                     str(self.game_master), 'Test': 'test'}):
            form = NpcForm(
                name='test',
                appearance='test',
                occupation='test',
                roleplaying='test',
                background='test',
                place_id=1
            )
            self.assertIsInstance(form, NpcForm)

    def test_create_npc_error(self):
        res = self.client().post('/npcs/create', headers={'Authorization':
                                 str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_edit_npc(self):
        with self.app.test_request_context(
            '/npcs/1/edit', headers={'Authorization':
                                     str(self.game_master), 'Test': 'test'}):
            form = NpcForm(
                name='test',
                appearance='test',
                occupation='test',
                roleplaying='test',
                background='test',
                place_id=1
            )
            self.assertIsInstance(form, NpcForm)

    def test_create_npc_error(self):
        res = self.client().post('/npcs/1/edit', headers={'Authorization':
                                 str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_delete_npc_error(self):
        res = self.client().post('/npcs/1/delete', headers={'Authorization':
                                 str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 405)

    # -------------------------------------------------------------------------#
    # Test: Place operations
    # -------------------------------------------------------------------------#

    def test_get_places(self):
        res = self.client().get('/places', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_get_places_error(self):
        res = self.client().get('/places', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_get_one_place(self):
        res = self.client().get('/places/1', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_get_one_place_error(self):
        res = self.client().get('/places/999999999', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_create_place(self):
        with self.app.test_request_context(
            '/places/create', headers={'Authorization':
                                       str(self.game_master), 'Test': 'test'}):
            form = PlaceForm(
                name='test',
                appearance='test',
                occupation='test',
                roleplaying='test',
                background='test',
                place_id=1
            )
            self.assertIsInstance(form, PlaceForm)

    def test_create_place_error(self):
        res = self.client().post('/places/create', headers={'Authorization':
                                 str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_edit_place(self):
        with self.app.test_request_context(
            '/npcs/1/edit', headers={'Authorization':
                                     str(self.game_master), 'Test': 'test'}):
            form = PlaceForm(
                name='test',
                appearance='test',
                occupation='test',
                roleplaying='test',
                background='test',
                place_id=1
            )
            self.assertIsInstance(form, PlaceForm)

    def test_create_place_error(self):
        res = self.client().post(
            '/places/1/edit', headers={'Authorization':
                                       str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_delete_place_error(self):
        res = self.client().post(
            '/places/1/delete',
            headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 405)

    # -------------------------------------------------------------------------#
    # Test: Get forms
    # -------------------------------------------------------------------------#

    def test_create_npc_form(self):
        res = self.client().get('/npcs/create', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_create_npc_form_error(self):
        res = self.client().get('/npcs/create', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_edit_npc_form(self):
        res = self.client().get('/npcs/1/edit', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_edit_npc_form_error(self):
        res = self.client().get('/npcs/999999/edit', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_create_place_form(self):
        res = self.client().get('/places/create', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_create_place_form_error(self):
        res = self.client().get('/places/create', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_edit_place_form(self):
        res = self.client().get('/places/1/edit', headers={'Authorization':
                                str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_edit_place_form_error(self):
        res = self.client().get(
            '/places/999999/edit',
            headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
