from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate()


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                    e.g. project.config.ProdConfig
    """
    cors = CORS(app)
    app.config.from_object(object_name)
    db.init_app(app)
    migrate.init_app(app, db)
    from .api import create_module as api_create_module
    api_create_module(app)
    
    return app