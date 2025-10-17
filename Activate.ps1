# ensure venv is active
. .\.venv\Scripts\Activate.ps1

python -m pytest -q --disable-warnings --maxfail=1
# or with coverage if pytest-cov is installed:
python -m pytest -q --disable-warnings --maxfail=1 --cov=. --cov-report=term
