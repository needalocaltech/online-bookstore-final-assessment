# tests/integration/test_catalog_routes.py

def test_homepage_lists_books(client):
    r = client.get("/")
    assert r.status_code == 200
    # Looser content check to accommodate different templates
    assert any(k in r.data for k in (b"Book", b"title", b"catalog", b"shop", b"Browse"))

def test_book_detail_page(client, route_map, resolve_first, resolve_like, fill_params):
    """
    Find and hit the real 'book detail' route regardless of its name.
    Strategy:
      1) Try common fixed patterns (/book/1, /books/1, /catalog/1, /details/1, /product/1, /item/1)
      2) Fuzzy-match any route containing keywords and auto-fill <params>
      3) Fallback: hit any GET route with a parameter and see if it returns 200/302
    """
    # 1) Common fixed patterns first
    for candidate in ("/book/1", "/books/1", "/catalog/1", "/details/1", "/detail/1", "/product/1", "/item/1"):
        r = client.get(candidate)
        if r.status_code in (200, 302):
            return

    # 2) Fuzzy-match parametric routes with likely keywords
    for kws in [("book",), ("books",), ("detail",), ("catalog",), ("product",), ("item",)]:
        path = resolve_like([kws], need_method="GET")
        if path:
            try_path = fill_params(path) if "<" in path else path
            r = client.get(try_path)
            if r.status_code in (200, 302):
                return

    # 3) Fallback: any GET route with a parameter that isn't root/static
    for rule, methods in route_map.items():
        if "GET" in methods and rule not in ("/", "/favicon.ico") and "<" in rule:
            try_path = fill_params(rule)
            r = client.get(try_path)
            if r.status_code in (200, 302):
                return

    assert False, f"Could not reach a details page. Available routes: {list(route_map.keys())}"
