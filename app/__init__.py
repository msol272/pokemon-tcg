from flask import Flask
from app.home import home_bp
from app.user import user_bp
from app.collection import collection_bp
from app.deck import deck_bp
from app.game import game_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bc6468914c825a0c824d79ab56d2110a'

    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(deck_bp)
    app.register_blueprint(game_bp)

    return app
