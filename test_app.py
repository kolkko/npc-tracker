import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

from app import create_app
from models import setup_db, Npc, Place
from forms import *

dm = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImpoSWFSYWdqMUxtU0pEazZESTJDdiJ9.eyJpc3MiOiJodHRwczovL2Rldi10ZXN0LWZzbmQuZXUuYXV0aDAuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTAyNzM1NDM5MDU1NTU5MTYyMTE5IiwiYXVkIjpbIm5wYy10cmFja2VyIiwiaHR0cHM6Ly9kZXYtdGVzdC1mc25kLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MTQxNjA0NTksImV4cCI6MTYxNDI0Njg1OSwiYXpwIjoiZHZiWEt0TDRqNHl1NEpMM2dRc1dzd3M3QndGSWxYUEYiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiYWRkOm5wYyIsImRlbGV0ZTpucGMiLCJlZGl0Om5wYyIsImdldDpucGNzIl19.a6-kT98_hRHYSRBwbxPru7mSyHU9vu5-_7j4VAprtQetw0PCVZUZyGSu84M1AFObRga4W4tnbJO4bq_KFvYRcUYAIw8zOL_ShB457Pjqp4L6t8aJSiKUHi7BnTX0F8etLxvuLEtILS430T6JXnyaGeJaRfuGhjxu8-2qHimdd12cmutxHVMXGYYDLLcQPzy2Sjq5P1gXgatBw8-TP11emZYonAgBy-uh0_ucJKrU9gTzmecNAyE5MG8LJlb9hs9ZNBEfVypUasNDjFeDoCufffYAE3IcSicQ4-z7d-mkgE2xrwu_mhm5OHLrUZgtobPE3cmvaHGCylXsByTqvwBYAg'

class NpcTrackerTestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  
        DB_USER = os.getenv('DB_USER', 'postgres')  
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')  
        DB_NAME = os.getenv('DB_NAME', 'npc_test')  
        DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME
        self.database_path = DB_PATH
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

# ----------------------------------------------------------------------------
# Test: GET /npcs 
# ----------------------------------------------------------------------------

    def test_get_npcs(self):
        print("Doing test")
        res = self.client().get('/npcs', headers={'Authorization': 'Bearer ' + dm})
        self.assertEqual(res.status_code, 200)

# ----------------------------------------------------------------------------
# Test: POST /npcs (success & error)
# ----------------------------------------------------------------------------

    # def test_create_npc(self):
    #     # New question details, for test
    #     with self.app.test_request_context():
    #         form = NpcForm(
    #             name = 'test',
    #             appearance = 'test',
    #             occupation = 'test',
    #             roleplaying = 'test',
    #             background = 'test',
    #             place_id = 1
    #         )
    #     print('NpcForm has been created')
    #     res = self.client().post('/npcs/create', form=form)
    #     print('RES ', res)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertTrue(data['npc_id']),

    # def test_error_400_create_question(self):
    #     json_test_question = {
    #         'answer': 'Test answer',
    #         'category': '1',
    #         'difficulty': 1
    #     }

    #     res = self.client().post('/questions', json=json_test_question)
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 400)
    #     self.assertEqual(data['success'], False)

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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
