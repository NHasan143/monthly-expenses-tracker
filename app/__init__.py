from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = 'dev-secret-key-change-in-production'

    from .routes import main
    app.register_blueprint(main)

    return app
