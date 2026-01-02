"""File to intiate the create_app function that will define application that flask
will run on. Regiesters the blueprints here as well.
"""

import os
from flask import (
    Flask,
    render_template,
    session,
    current_app,
    send_from_directory,
    request,
    redirect,
    url_for,
)
from datetime import timedelta
import traceback
from config import config
from .views.index.routes import main
from flask_cors import CORS

from .extensions import bcrypt
from .extensions import exe
from .extensions import secure_headers
from .extensions import csrf


def register_blueprints_on_app(app):
    """All blueprints for app are registered here. Can pass in as many as neeed.
    follow the "main" blueprint for example on folder setup. They are located in
    the views folder

    Args:
        app ([type]): <class 'flask.app.Flask'> testing gihub commits
    """
    app.register_blueprint(main)


def create_app(config_env=os.getenv("ENV"), register_blueprints=True):
    """creates an app, which is an instance of Flask. Flask is a lightweight WSGI
    web application framework.

    Args:
        config_env ([type], optional): [description]. Defaults to os.getenv('ENV').

    Returns:
        <class 'flask.app.Flask'>:
    """

    app = Flask(__name__)
    app.config.from_object(config[config_env])

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': app.config.get("POOL_RECYCLE", 60)
    }

    # Initialize extensions
    bcrypt.init_app(app)
    exe.init_app(app)
    csrf.init_app(app)

    # CORS
    CORS(app, supports_credentials=True)

    @app.before_request
    def make_session_permanent():
        session.permanent = app.config.get("PERMANENT", True)

    @app.after_request
    def set_secure_headers(response):
        secure_headers.framework.flask(response)
        return response

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(current_app.root_path, "static"),
            "favicon.ico",
            mimetype="image/x-icon",
        )

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        error_msg = traceback.format_exc()
        return render_template(
            "500.html",
            error=error_msg
        ), 500

    @app.context_processor
    def get_route():
        try:
            route_name = request.url_rule.rule
        except Exception:
            route_name = "/home"
        return dict(route_name=route_name)

    if register_blueprints:
        register_blueprints_on_app(app)

    return app
