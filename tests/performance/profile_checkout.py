# tests/performance/profile_checkout.py
import cProfile, pstats, io, pathlib
from app_old import app

out_dir = pathlib.Path("evidence/perf")
out_dir.mkdir(parents=True, exist_ok=True)
prof_path = out_dir / "profile_checkout.prof"

def run_checkout():
    c = app.test_client()
    with c:
        # add something to cart first
        for path in ("/cart/add", "/add_to_cart"):
            r = c.post(path, data={"book_id": "1", "qty": 2})
            if r.status_code in (200, 302): break
        # then checkout (try common paths)
        for path in ("/checkout", "/order/checkout"):
            r = c.post(path, data={
                "name": "Alex",
                "email": "alex@example.com",
                "address": "1 Street",
                "card": "4242424242424242",
                "voucher": "SAVE10"
            })
            if r.status_code in (200, 302): break

if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    run_checkout()
    pr.disable()
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("cumtime").print_stats(30)
    with open(out_dir / "profile_checkout.txt", "w") as f:
        f.write(s.getvalue())
    pr.dump_stats(str(prof_path))
    print(f"✅ Wrote {prof_path.resolve()} and {str(out_dir / 'profile_checkout.txt')}")
