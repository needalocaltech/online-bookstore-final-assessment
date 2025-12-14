. .\.venv\Scripts\Activate.ps1
python -m pytest -q --disable-warnings --maxfail=1
# (optional coverage)
python -m pytest -q --disable-warnings --maxfail=1 --cov=. --cov-report=term
