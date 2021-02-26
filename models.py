import os
from sqlalchemy import Column, String, Integer, create_engine, Boolean
from flask_sqlalchemy import SQLAlchemy
import json

# DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  
# DB_USER = os.getenv('DB_USER', 'postgres')  
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')  
# DB_NAME = os.getenv('DB_NAME', 'npc_test')  
# DATABASE_URL = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

DATABASE_URL = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=DATABASE_URL):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

'''
NPC
'''
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

  def __init__(self, name, appearance, occupation, roleplaying, background, place_id, user_id):
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
    print('about to commit')
    db.session.commit()
    print('committed')
  
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

'''
PLACES
'''
class Place(db.Model):  
  __tablename__ = 'places'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  location = Column(String)
  description = Column(String)
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

# '''
# STAT BLOCK
# '''
# class Stat_block(db.Model):  
#   __tablename__ = 'stat_blocks'

#   id = Column(Integer, primary_key=True)
#   strength = Column(Integer)
#   dexterity = Column(Integer)
#   constitution = Column(Integer)
#   intelligence = Column(Integer)
#   wisdom = Column(Integer)
#   charisma = Column(Integer)

#   def __init__(self, new_stat_block):
#     self.strength = new_stat_block['str']
#     self.dexterity = new_stat_block['dex']
#     self.constitution = new_stat_block['con']
#     self.intelligence = new_stat_block['int']
#     self.wisdom = new_stat_block['wis']
#     self.charisma = new_stat_block['charisma']

#   def format(self):
#     return {
#       'id': self.id,
#       'str': self.strength,
#       'dex': self.dexterity,
#       'con': self.constitution,
#       'int': self.intelligence,
#       'wis': self.wisdom,
#       'cha': self.charisma

#     }