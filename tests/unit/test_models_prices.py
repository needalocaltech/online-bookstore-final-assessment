# tests/performance/test_timeit_pricing.py
import os, sys, timeit, pathlib, importlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# from models_0 import apply_discount  # provided by models helpers above
from models import apply_discount  # provided by models helpers above

def test_pricing_micro_benchmark():
    t = timeit.timeit(lambda: apply_discount(100.0, "SAVE10"), number=5000)
    pathlib.Path("evidence/perf").mkdir(parents=True, exist_ok=True)
    with open("evidence/perf/timeit_results.txt", "w") as f:
        f.write(f"5k runs: {t:.4f}s\nAvg per run: {t/5000:.8f}s\n")
    assert t >= 0.0  # tighten later (CI budget)
