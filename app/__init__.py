from flask import Flask
from .chat_settings import get_chat_settings, update_chat_settings

def create_app():
    app = Flask(__name__)
    from .app import app as main_app
    app.register_blueprint(main_app)
    return app

