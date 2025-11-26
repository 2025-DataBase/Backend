# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"  # CSRF, flash 등에 필요

    from .routes import bp
    app.register_blueprint(bp)

    return app
