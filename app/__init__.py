from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.news import bp as news_bp
    app.register_blueprint(news_bp, url_prefix='/news')

    return app
