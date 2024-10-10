from flask import Flask
from app.home import home_bp
from app.users import users_bp
from app.collection import collection_bp
from app.deck import deck_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bc6468914c825a0c824d79ab56d2110a'

    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(deck_bp)

    return app
