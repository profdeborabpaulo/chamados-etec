"""Fábrica de aplicação Flask (Application Factory) integrada ao SQLAlchemy e Flask-Login."""

from flask import Flask
from flask_login import current_user
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """Inicializa e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)

    # Carregador de usuário para o Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Context processor para expor 'logged_user' a todos os templates Jinja2
    @app.context_processor
    def inject_user():
        return {
            'logged_user': current_user if current_user.is_authenticated else None
        }

    # Registro de Blueprints
    from app.routes.auth import auth_bp
    from app.routes.chamados import chamados_bp
    from app.routes.usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chamados_bp)
    app.register_blueprint(usuarios_bp)

    return app
