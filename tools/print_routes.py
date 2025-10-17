from app import app

print("=== URL MAP ===")
for r in app.url_map.iter_rules():
    methods = ",".join(sorted(r.methods))
    print(f"{str(r):35s} methods=[{methods}] endpoint={r.endpoint}")
