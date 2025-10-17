import cProfile, pstats, io, pathlib
from app import app

out_dir = pathlib.Path("evidence/perf")
out_dir.mkdir(parents=True, exist_ok=True)
prof_path = out_dir / "profile_checkout.prof"

def run_checkout():
    c = app.test_client()
    with c:
        c.post("/cart/add", data={"book_id": "1", "qty": 2})
        c.post("/checkout", data={
            "name": "agne",
            "email": "agne@example.com",
            "address": "1 Street",
            "card": "4242424242424242",
            "voucher": "SAVE10"
        })

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
    print(f"✅ Profile written to {prof_path.resolve()}")
