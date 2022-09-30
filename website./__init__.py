from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import csv
from graph import Graph
from csvReader import populateGraph






db = SQLAlchemy()
DB_NAME = "database.db"
global graph

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    populateGraph("weekday")
    populateGraph("saturday")
    populateGraph("sunday_holiday")

    from .views import views
    from .views import populateStationsDb
    from .auth import auth

    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, SavedSearch

    create_database(app)


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        from website.views import populateStationsDb
        db.create_all(app=app)
        populateStationsDb()
        print('Created Database!')
