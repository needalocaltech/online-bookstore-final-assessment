def test_imports():
    import app_old, models_not_quite_working
    # app.app should be the Flask instance
    assert hasattr(app_old, "app")
