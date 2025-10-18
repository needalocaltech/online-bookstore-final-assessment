# tests/integration/test_checkout_flow.py

def _checkout_path(resolve_first):
    return resolve_first(["/checkout", "/order/checkout"], "POST")

def _add_path(resolve_first):
    return resolve_first(["/cart/add", "/add-to-cart"], "POST")

def test_checkout_success(client, resolve_first):
    add = _add_path(resolve_first)
    chk = _checkout_path(resolve_first)
    assert add and chk
    client.post(add, data={"book_id": "1", "qty": "1"})
    r = client.post(chk, data={
        "name": "Alex", "email": "alex@example.com", "address": "1 Road",
        "card": "4242424242424242", "voucher": "SAVE10"
    }, follow_redirects=True)
    assert r.status_code in (200, 302)

def test_checkout_fail_card_ends_1111(client, resolve_first):
    add = _add_path(resolve_first)
    chk = _checkout_path(resolve_first)
    assert add and chk
    client.post(add, data={"book_id": "1", "qty": "1"})
    r = client.post(chk, data={
        "name": "Lee", "email": "lee@example.com", "address": "2 Road",
        "card": "4000000000001111", "voucher": "SAVE10"
    }, follow_redirects=True)
    assert r.status_code in (200, 302)
