# tests/integration/conftest.py
import os, sys, pathlib, importlib
import pytest

# Ensure project root (folder that holds app.py) is importable
ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../project/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _load_flask_app():
    """
    Try common module/attribute names, e.g., app.py exposing 'app'.
    Edit candidates if your file/variable is different.
    """
    candidates = [
        ("app", "app"),    # app.py -> app (Flask instance)
        ("main", "app"),   # main.py  -> app
        ("wsgi", "app"),   # wsgi.py  -> app
    ]
    for mod_name, attr in candidates:
        try:
            mod = importlib.import_module(mod_name)
            flask_app = getattr(mod, attr)
            return flask_app
        except Exception:
            continue
    raise ImportError(
        "Could not import the Flask app instance. "
        "Ensure your project has app.py defining `app = Flask(__name__)` "
        "or update candidates in conftest.py."
    )

@pytest.fixture(scope="session")
def app():
    flask_app = _load_flask_app()
    flask_app.config.update(TESTING=True)
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
