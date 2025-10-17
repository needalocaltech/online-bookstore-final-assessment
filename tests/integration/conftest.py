# tests/integration/conftest.py
import os, sys, pathlib, importlib
import pytest

# Ensure project root (folder holding app.py/models.py) is importable
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _load_flask_app():
    """Try common module/attribute names, e.g., app.py exposing 'app'."""
    candidates = [
        ("app", "app"),    # app.py -> app (Flask instance)
        ("main", "app"),   # main.py -> app
        ("wsgi", "app"),   # wsgi.py -> app
    ]
    for mod_name, attr in candidates:
        try:
            mod = importlib.import_module(mod_name)
            return getattr(mod, attr)
        except Exception:
            continue
    raise ImportError(
        "Could not import Flask app instance. "
        "Ensure your project has app.py defining `app = Flask(__name__)` "
        "or update candidates in conftest.py."
    )

@pytest.fixture(scope="session")
def app():
    flask_app = _load_flask_app()
    flask_app.config.update(TESTING=True)
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def route_map(app):
    """Return {path: methods} for resolving real endpoints."""
    return {str(r): r.methods for r in app.url_map.iter_rules()}

@pytest.fixture
def resolve_first(route_map):
    """
    Fixture that returns a resolver callable.
    Usage in tests:  path = resolve_first(["/cart/add", "/add_to_cart"], "POST")
    """
    def _resolve(candidates, need_method=None):
        for c in candidates:
            for rule, methods in route_map.items():
                if rule == c and (need_method is None or need_method in methods):
                    return c
        return None
    return _resolve
