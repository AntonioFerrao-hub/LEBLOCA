from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from .config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class: type[Config] | None = None) -> Flask:
    """Application factory for the Google review management platform."""

    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class or Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from .auth import auth_bp
    from .google_accounts import google_accounts_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(google_accounts_bp, url_prefix="/api/google-accounts")

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    return app


__all__ = ["create_app", "db", "bcrypt", "jwt"]
