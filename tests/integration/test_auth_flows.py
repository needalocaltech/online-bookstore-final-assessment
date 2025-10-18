# tests/integration/test_auth_flows.py
def test_register_login_logout(client):
    # register
    r = client.post("/register", data={
        "email": "newuser@example.com",
        "password": "test123",
        "confirm": "test123"
    }, follow_redirects=True)
    assert r.status_code in (200, 302)

    # login
    r = client.post("/login", data={
        "email": "newuser@example.com",
        "password": "test123"
    }, follow_redirects=True)
    assert r.status_code in (200, 302)
    # be resilient: look for common post-login markers
    ok_signals = [b"Logout", b"Sign out", b"My Orders", b"Account", b"Welcome", b"Profile"]
    assert any(sig in r.data for sig in ok_signals), \
        "Login succeeded but expected UI markers not found."

    # logout
    r = client.get("/logout", follow_redirects=True)
    assert r.status_code == 200
