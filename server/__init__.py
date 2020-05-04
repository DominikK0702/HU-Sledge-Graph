import uuid

from flask import Flask


def configure_app(app):
    app.config['SECRET_KEY'] = uuid.uuid4().hex
    return app


def register_blueprints(app):
    from server.bp import graph_bp
    app.register_blueprint(graph_bp)
    return app


def create_app():
    app = configure_app(Flask(__name__, instance_relative_config=False))
    register_blueprints(app)
    return app
