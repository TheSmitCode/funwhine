# FunWhine — FastAPI Starter (Local dev)

This repo is the FunWhine Phase 1 scaffold (FastAPI).  
It is designed to run locally (SQLite) and in Docker (Postgres recommended for production).

**Important**: When replacing files, paste full-file contents — do not paste snippets.

---

## Quick dev setup (Windows PowerShell)

1. Create & activate venv (Python 3.11/3.12 recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
Install requirements

powershell
Copy code
pip install --upgrade pip
pip install -r requirements.txt
(Optional) Create .env to override defaults:

ini
Copy code
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=change-me
Run Alembic (generate + apply) after models change:

powershell
Copy code
# generate (if you change models)
alembic revision --autogenerate -m "describe change"

# apply
alembic upgrade head
Run the app (dev)

powershell
Copy code
uvicorn app.main:app --reload --port 8000
Docker

powershell
Copy code
docker build -t funwhine .
docker run --name funwhine-container -p 8000:8000 funwhine
Notes & troubleshooting
If you see ModuleNotFoundError: No module named 'jwt' install python-jose:

powershell
Copy code
pip install python-jose
If Alembic errors on import, ensure alembic.ini has script_location = alembic and your alembic/env.py imports app.db using package imports (not relative file paths).

Keep your requirements.txt updated. For development you may want a requirements-dev.txt with pytest, ipython, etc.

Development philosophy
Start with SQLite locally, then switch to Postgres in the docker-compose when ready.

Keep code explicit — prefer full-file replacements for maintainability.

I will supply full replacements for every file you ask; after you paste these core files, run the thin test suite described above and send me back logs/errors and I will continue.

yaml
Copy code

---

## What I changed and why (summary)

- `config.py` — moved to `pydantic-settings` usage to avoid BaseSettings import errors.
- `schemas.py` — explicit Pydantic v2 `from_attributes` configuration, full shape of input/output models.
- `__init__.py` — minimal but safe package exports.
- `README.md` — updated dev instructions and quick troubleshooting (uses python-jose for JWTs).

---

## After you paste these files

Run these quick checks (copy-paste to your terminal in project root):

```powershell
# Ensure virtualenv activated
python -V

# Quick smoke: run the app locally
uvicorn app.main:app --reload --port 8000
```