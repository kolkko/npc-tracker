from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp



class NpcForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    appearance = StringField(
        'appearance', validators=[]
    )
    place_id = SelectField(
        'place_id', validators=[],
    )
    occupation = StringField(
        'occupation', validators=[]
    )
    roleplaying = StringField(
        'roleplaying', validators=[],
    )
    background = StringField(
        'background', validators=[]
    )
    # genres = SelectMultipleField(
    #     'genres', validators=[DataRequired()],
    #     choices=[
    #         ('Alternative', 'Alternative'),
    #         ('Blues', 'Blues'),
    #         ('Classical', 'Classical'),
    #         ('Country', 'Country'),
    #         ('Electronic', 'Electronic'),
    #         ('Folk', 'Folk'),
    #         ('Funk', 'Funk'),
    #         ('Hip-Hop', 'Hip-Hop'),
    #         ('Heavy Metal', 'Heavy Metal'),
    #         ('Instrumental', 'Instrumental'),
    #         ('Jazz', 'Jazz'),
    #         ('Musical Theatre', 'Musical Theatre'),
    #         ('Pop', 'Pop'),
    #         ('Punk', 'Punk'),
    #         ('R&B', 'R&B'),
    #         ('Reggae', 'Reggae'),
    #         ('Rock n Roll', 'Rock n Roll'),
    #         ('Soul', 'Soul'),
    #         ('Other', 'Other'),
    #     ]
    # )
    # facebook_link = StringField(
    #     'facebook_link', validators=[URL()]
    # )

