def test_imports():
    # import app_old, models_not_quite_working
    import app_old, models
    # app.app should be the Flask instance
    assert hasattr(app_old, "app")
