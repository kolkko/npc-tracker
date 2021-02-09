import os
from sqlalchemy import Column, String, Integer, create_engine, Boolean
from flask_sqlalchemy import SQLAlchemy
import json

# DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  
# DB_USER = os.getenv('DB_USER', 'postgres')  
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'a')  
# DB_NAME = os.getenv('DB_NAME', 'npc_test')  
# DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

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

  id = Column(Integer, primary_key=True)
  name = Column(String)
  appearance = Column(String)
  image = Column(String)
  quote = Column(String)
  roleplaying = Column(String)
  background = Column(String)
  all_info = db.relationship('Information', backref='npc', lazy=True)

  def __init__(self, name, appearance, image, quote, roleplaying, background):
    self.name = name
    self.appearance = appearance
    self.image = image
    self.quote = quote
    self.roleplaying = roleplaying
    self.background = background

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
      'image': self.image,
      'quote': self.quote,
      'roleplaying': self.roleplaying,
      'background': self.background
    }

'''
PLOT_POINTS
'''
class Information(db.Model):  
  __tablename__ = 'information'

  id = Column(Integer, primary_key=True)
  detail = Column(String)
  revealed = Column(Boolean)
  npc_id = Column(Integer, db.ForeignKey('npcs.id'))

  def __init__(self, new_npc_details):
    self.name = new_npc_details['name']
    self.appearance = new_npc_details['appearance']
    self.image = new_npc_details['image']
    self.background = new_npc_details['background']

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
      'image': self.image,
      'background': self.background
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