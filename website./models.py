from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

#this model is used to store previous searches of users
class SavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    departureStation = db.Column(db.String(150))
    destinationStation = db.Column(db.String(150))
    searchBy = db.Column(db.String(150))
    time = db.Column(db.String(150))
    day = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#this model is used to store the station names along with their coordinates
class Stations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

#this model is used to store user details
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    admin_status = db.Column(db.String(150))
    savedSearches = db.relationship('SavedSearch')
