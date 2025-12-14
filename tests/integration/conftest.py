# tests/integration/conftest.py
import os, sys, pathlib, importlib, re
import pytest
import flask
from flask import flask, render_template, request, redirect, url_for, flash, jsonify, session



# ROOT = pathlib.Path(__file__).resolve().parents[2]
# ROOT = pathlib.Path(__file__).resolve().parents[2]
ROOT = "../../../"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _load_flask_app():
    for mod_name, attr in [("app","app"), ("main","app"), ("wsgi","app")]:
        try:
            mod = importlib.import_module(mod_name)
            return getattr(mod, attr)
        except Exception:
            continue
    raise ImportError("Flask app not found: expected app.py/main.py/wsgi.py exposing `app`.")

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
    return {str(r): r.methods for r in app.url_map.iter_rules()}

@pytest.fixture
def resolve_first(route_map):
    def _resolve(candidates, need_method=None):
        for c in candidates:
            for rule, methods in route_map.items():
                if rule == c and (need_method is None or need_method in methods):
                    return c
        return None
    return _resolve

@pytest.fixture
def resolve_like(route_map):
    def _resolve(keyword_groups, need_method=None):
        for rule, methods in route_map.items():
            path = rule.replace('-', '/').lower()
            for kws in keyword_groups:
                if all(k.lower() in path for k in kws):
                    if need_method is None or need_method in methods:
                        return rule
        return None
    return _resolve

@pytest.fixture
def fill_params():
    def _fill(rule: str):
        def repl(m):
            name = (m.group(1) or m.group(2) or "").lower()
            if "qty" in name or "quantity" in name:
                return "2"
            return "1"
        return re.sub(r"<(?:[^:>]*:)?([^>]+)>", repl, rule)
    return _fill
