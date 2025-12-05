import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from flask_wtf.csrf import CSRFProtect, generate_csrf

from config import CONFIG_BY_NAME, ProductionConfig
from db import db
from services import user_service, book_service, cart_service, order_service

csrf = CSRFProtect()


def create_app(config_name: str | None = None) -> Flask:
    """
    Main application factory for the online bookstore.
    """
    app = Flask(__name__, instance_relative_config=False)

    # Decide which config to use
    env = config_name or os.environ.get("FLASK_ENV", "development")
    config_cls = CONFIG_BY_NAME.get(env, CONFIG_BY_NAME["development"])
    app.config.from_object(config_cls)

    # In production, fail fast if insecure defaults are used
    if isinstance(config_cls, type) and issubclass(config_cls, ProductionConfig):
        config_cls.validate()

    # Initialise database
    db.init_app(app)

    # Enable CSRF protection on all modifying requests
    csrf.init_app(app)

    # ---------------------------------------------------------
    # MAKE CSRF TOKEN AVAILABLE IN ALL JINJA TEMPLATES
    # ---------------------------------------------------------
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # --- Logging / audit trail (rotating log file) ---
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    handler = RotatingFileHandler(
        log_dir / "bookstore.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    logging.getLogger().addHandler(handler)

    # --- Initialise DB schema and seed demo data / in-memory stores ---
    with app.app_context():
        db.create_all()
        user_service.init_demo_user()
        book_service.init_books()
        cart_service.init_cart()
        order_service.init_store()

    # --- Register blueprints (routes/controllers layer) ---
    from routes.store import store_bp
    from routes.cart import cart_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(store_bp)                 # '/', book listing
    app.register_blueprint(cart_bp)                  # '/cart', '/add-to-cart', ...
    app.register_blueprint(auth_bp)                  # '/login', '/register'
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # --- Basic security headers on every response ---
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; "
            "script-src 'self'; style-src 'self' 'unsafe-inline'"
        )
        return response

    return app
