def test_imports():
    import app, models
    # app.app should be the Flask instance
    assert hasattr(app, "app")
