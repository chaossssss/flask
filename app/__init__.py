from flask import Flask
from flask_cors import CORS
from config import Config


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object("config.Config")

    from . import routes

    app.register_blueprint(routes.bp)

    return app
