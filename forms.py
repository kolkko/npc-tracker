from datetime import datetime
from flask_wtf import Form
from wtforms import (StringField, SelectField, SelectMultipleField,
                     DateTimeField, BooleanField, IntegerField, DateTimeField)
from wtforms.validators import DataRequired, AnyOf, URL, Regexp


class NpcForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    appearance = StringField(
        'appearance', validators=[]
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
    place_id = SelectField(
        'place_id', validators=[], coerce=str
    )
    # genres = SelectMultipleField(
    #     'genres', validators=[DataRequired()],
    #     choices=[
    #         ('Alternative', 'Alternative'),
    #         ('Blues', 'Blues'),
    #         ('Classical', 'Classical'),
    #     ]
    # )
    # facebook_link = StringField(
    #     'facebook_link', validators=[URL()]
    # )


class PlaceForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    location = StringField(
        'location', validators=[]
    )
    description = StringField(
        'description', validators=[]
    )
