# tests/integration/test_cart_routes.py

def test_add_to_cart(client, resolve_first):
    path = resolve_first(["/cart/add", "/add_to_cart", "/add-to-cart", "/cart/add_item"], "POST")
    assert path, "No matching add-to-cart route found."
    r = client.post(path, data={"book_id": "1", "qty": "2"}, follow_redirects=True)
    assert r.status_code in (200, 302)

def test_update_cart_qty(client, resolve_first):
    add_path = resolve_first(["/cart/add", "/add_to_cart", "/add-to-cart"], "POST")
    upd_path = resolve_first(["/cart/update", "/update_cart", "/update-cart"], "POST")
    assert add_path and upd_path
    client.post(add_path, data={"book_id": "1", "qty": "1"})
    r = client.post(upd_path, data={"book_id": "1", "qty": "3"}, follow_redirects=True)
    assert r.status_code in (200, 302)

def test_remove_from_cart(client, resolve_first):
    add_path = resolve_first(["/cart/add", "/add_to_cart", "/add-to-cart"], "POST")
    rem_path = resolve_first(["/cart/remove", "/remove_from_cart","/remove-from-cart"], "POST")
    assert add_path and rem_path
    client.post(add_path, data={"book_id": "1", "qty": "1"})
    r = client.post(rem_path, data={"book_id": "1"}, follow_redirects=True)
    assert r.status_code in (200, 302)
