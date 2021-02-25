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

# dm = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImpoSWFSYWdqMUxtU0pEazZESTJDdiJ9.eyJpc3MiOiJodHRwczovL2Rldi10ZXN0LWZzbmQuZXUuYXV0aDAuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTAyNzM1NDM5MDU1NTU5MTYyMTE5IiwiYXVkIjpbIm5wYy10cmFja2VyIiwiaHR0cHM6Ly9kZXYtdGVzdC1mc25kLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MTQxNzg2MzIsImV4cCI6MTYxNDI2NTAzMiwiYXpwIjoiZHZiWEt0TDRqNHl1NEpMM2dRc1dzd3M3QndGSWxYUEYiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiYWRkOm5wYyIsImRlbGV0ZTpucGMiLCJlZGl0Om5wYyIsImdldDpucGNzIl19.NShPnh-KEMcW-Hp-itc91PInzEgoN1lRl5KHb8eealPpuBlCwhwHVJRd8OG9ROA-HQvfxMNSjELyOP0NREnyrFmsEeBCHA7iPwR_YQ9FN7ouJS7GxC5bgCyokz7fEUKyWrbT_ej7tUUXREKLrT0zBhYhWVTyNF1VCBYVqUB9NbQpCBRY1TgOUWuOlsq9B4tYd_9ZzQu_A6dziarx54hLEt8iXd8dtxyFOIEVoL0xthUOEGa4Glf2jXc51Cr-H4dfx7f5gNB89fGAMj-kY5mCKEOQOwHFFZgujqmWpDdyJ7-qtc4uFskL0X8PsTSBw4t4C1UaQj8jGHhlCo1j2Dgc3w'

class NpcTrackerTestCase(unittest.TestCase):

    # runs before each test
    def setUp(self):
        DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  
        DB_USER = os.getenv('DB_USER', 'postgres')  
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')  
        DB_NAME = os.getenv('DB_NAME', 'npc_test')  
        DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

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

    # ----------------------------------------------------------------------------
    # Test: Home 
    # ----------------------------------------------------------------------------

    def test_home(self):
        res = self.client().get('/')
        self.assertEqual(res.status_code, 200)

    def test_home_error(self):
        res = self.client().get('/wrong')
        self.assertEqual(res.status_code, 404)
    
    def test_logged_in(self):
        res = self.client().get('/logged-in', headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_logged_in_error(self):
        res = self.client().get('/logged-in', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    # ----------------------------------------------------------------------------
    # Test: GET NPCs
    # ----------------------------------------------------------------------------
    
    def test_get_npcs(self):
        res = self.client().get('/npcs', headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_get_npcs_error(self):
        res = self.client().get('/npcs', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_get_one_npc(self):
        res = self.client().get('/npcs/1', headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_get_one_npc_error(self):
        res = self.client().get('/npcs/999999999', headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    # ----------------------------------------------------------------------------
    # Test: POST /npcs (success & error)
    # ----------------------------------------------------------------------------

    def test_create_npc(self):
        # New question details, for test
        with self.app.test_request_context('/npcs/create',
                    headers={'Authorization': str(self.game_master), 'Test': 'test'}):
            form = NpcForm(
                name = 'test',
                appearance = 'test',
                occupation = 'test',
                roleplaying = 'test',
                background = 'test',
                place_id = 1
            )
            res = self.client().post('/npcs/create',
                    headers={'Authorization': str(self.game_master), 'Test': 'test'})
            self.assertIsInstance(form, NpcForm)
            self.assertEqual(res.status_code, 200)

    def test_create_npc_error(self):
        res = self.client().post('/npcs/create',
                    headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)


# ----------------------------------------------------------------------------
# Test: DELETE /npcs (success & error)
# ----------------------------------------------------------------------------

    # def test_delete_npc(self):
    #     # Create a new question, so that it can be deleted
    #     json_test_npc = {
    #         'name': 'Data for deleting',
    #         'appearance': 'test',
    #         'occupation': 'test',
    #         'roleplaying': 'test',
    #         'background': 'test',
    #         'place_id': 1
    #     }
    #     res = self.client().post('/npcs/create', json=json_test_npc)
    #     data = json.loads(res.data)
    #     print('NPC ID', data)

    #     # Test the DELETE request by deleting the new question
    #     res = self.client().delete('/npcs/{}'.format(npc_id))
    #     print("Res: ", res)
    #     data = json.loads(res.data)
    #     # print(data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['deleted'])

    # def test_error_400_delete_question(self):
    #     """Try to delete an non-existant ID"""
    #     res = self.client().delete('/questions/{}'.format(9999))
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 400)
    #     self.assertEqual(data['success'], False)

    # ----------------------------------------------------------------------------
    # Test: Get forms to create resources
    # ----------------------------------------------------------------------------
    # def test_edit_npc_form(self):
    #     res = self.client().get('/npcs/1/edit')
    #     self.assertEqual(res.status_code, 200)
    
    # def test_edit_npc_form_error(self):
    #     res = self.client().get('/npcs/999999999/edit')
    #     self.assertEqual(res.status_code, 400)

    # def test_create_npc_form(self):
    #     res = self.client().get('/npcs/create')
    #     self.assertEqual(res.status_code, 200)

    # def test_create_npc_form_error(self):
    #         res = self.client().patch('/npcs/create')
    #         self.assertEqual(res.status_code, 405)

    # def test_edit_place_form(self):
    #     res = self.client().get('/places/1/edit')
    #     self.assertEqual(res.status_code, 200)

    # def test_edit_place_form_error(self):
    #     res = self.client().get('/places/999999999/edit')
    #     self.assertEqual(res.status_code, 400)

    # def test_create_place_form(self):
    #     res = self.client().get('/places/create')
    #     self.assertEqual(res.status_code, 200)

    # def test_create_place_form_error(self):
    #     res = self.client().patch('/places/create')
    #     self.assertEqual(res.status_code, 405)

    # ----------------------------------------------------------------------------
    # Test: GET Places
    # ----------------------------------------------------------------------------
    
    def test_get_places(self):
        res = self.client().get('/places', headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_get_places_error(self):
        res = self.client().get('/places', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_get_one_place(self):
        res = self.client().get('/places/1',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)

    def test_get_one_place_error(self):
        res = self.client().get('/places/999999999',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    # ----------------------------------------------------------------------------
    # Test: Create resources
    # ----------------------------------------------------------------------------
    
    def test_create_npc_form(self):
        res = self.client().get('/npcs/create',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_create_npc_form_error(self):
        res = self.client().get('/npcs/create', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_edit_npc_form(self):
        res = self.client().get('/npcs/1/edit',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_edit_npc_form_error(self):
        res = self.client().get('/npcs/999999/edit',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_create_place_form(self):
        res = self.client().get('/places/create',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_create_place_form_error(self):
        res = self.client().get('/places/create', headers={'Test': 'test'})
        self.assertEqual(res.status_code, 401)

    def test_edit_place_form(self):
        res = self.client().get('/places/1/edit',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 200)
    
    def test_edit_place_form_error(self):
        res = self.client().get('/places/999999/edit',
                headers={'Authorization': str(self.game_master), 'Test': 'test'})
        self.assertEqual(res.status_code, 401)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
