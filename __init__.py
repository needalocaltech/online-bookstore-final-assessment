import os
from flask import Flask
from .config import CONFIG_BY_NAME
from flask_wtf.csrf import CSRFProtect

# Services
from .services import user_service, book_service, cart_service, order_service

csrf = CSRFProtect()

def create_app(config_name: str | None = None) -> Flask:
    """
    Application factory.

    Usage:
        app = create_app()                   # uses FLASK_ENV or 'development'
        app = create_app("production")       # explicit
    """
    app = Flask(__name__, instance_relative_config=False)
    

    # Decide which config to use
    env = config_name or os.environ.get("FLASK_ENV", "development")
    config_cls = CONFIG_BY_NAME.get(env, CONFIG_BY_NAME["development"])
    app.config.from_object(config_cls)

    # --- Initialise core domain/services ---
    user_service.init_demo_user()
    book_service.init_books()
    cart_service.init_cart()
    order_service.init_store()

    # --- Register blueprints (routes/controllers layer) ---
    from .routes.store import store_bp
    from .routes.cart import cart_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.api import api_bp

    app.register_blueprint(store_bp)                # '/', book listing
    app.register_blueprint(cart_bp)                 # '/cart', '/checkout', etc.
    app.register_blueprint(auth_bp)                 # '/login', '/register', '/account'
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Enable CSRF protection on all modifying requests
    csrf.init_app(app)

    return app
