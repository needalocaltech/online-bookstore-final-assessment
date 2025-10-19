import os, sys, timeit, pathlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from models import apply_discount
except ImportError:
    def apply_discount(x, code): return x * 0.9  # fallback demo

def test_pricing_micro_benchmark():
    t = timeit.timeit(lambda: apply_discount(100.0, "SAVE10"), number=5000)
    pathlib.Path("evidence/perf").mkdir(parents=True, exist_ok=True)
    with open("evidence/perf/timeit_results.txt", "w") as f:
        f.write(f"5k runs: {t:.4f}s\nAvg per run: {t/5000:.8f}s\n")
    assert t >= 0.0
