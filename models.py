import os
from sqlalchemy import Column, String, Integer, create_engine, Boolean
from flask_sqlalchemy import SQLAlchemy
import json

# DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
# DB_USER = os.getenv('DB_USER', 'postgres')
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')
# DB_NAME = os.getenv('DB_NAME', 'npc_test')
# DATABASE_URL = ('postgresql+psycopg2://{}:{}@{}/{}'.
#                 format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME))

DATABASE_URL = os.environ['DATABASE_URL']

db = SQLAlchemy()


# -------------------------------------------------------------------------#
# Bind flask application with a SQLAlchemy service
# -------------------------------------------------------------------------#

def setup_db(app, database_path=DATABASE_URL):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


# -------------------------------------------------------------------------#
# NPC model
# -------------------------------------------------------------------------#

class Npc(db.Model):
    __tablename__ = 'npcs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    appearance = db.Column(db.String)
    occupation = db.Column(db.String)
    roleplaying = db.Column(db.String)
    background = db.Column(db.String)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'))
    user_id = db.Column(db.String)

    def __init__(self, name, appearance, occupation,
                 roleplaying, background, place_id, user_id):
        print('creating new npc')
        self.name = name
        self.appearance = appearance
        self.occupation = occupation
        self.roleplaying = roleplaying
        self.background = background
        self.place_id = place_id
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'appearance': self.appearance,
            'occupation': self.occupation,
            'roleplaying': self.roleplaying,
            'background': self.background,
            'user_id': self.user_id
        }


# -------------------------------------------------------------------------#
# Place model
# -------------------------------------------------------------------------#

class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    location = db.Column(db.String)
    description = db.Column(db.String)
    all_npcs = db.relationship('Npc', backref='place', lazy=True)
    user_id = db.Column(db.String)

    def __init__(self, name, location, description, user_id):
        self.name = name
        self.location = location
        self.description = description
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'user_id': self.user_id
        }
