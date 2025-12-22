# Crypto Portfolio Dashboard

A full-stack **cryptocurrency portfolio dashboard** that combines:
- **FastAPI + SQLAlchemy** backend (REST API)
- **Dash + Plotly** frontend (interactive dashboard)
- **SQLite** database by default (local file: `crypto_portfolio.db`)

Use it to track your holdings (quantity, purchase price, current price), view portfolio performance, visualize charts, and manage holdings from the UI.

---

## Highlights

- Portfolio metrics: **total value**, **total invested**, **gain/loss**, **return %**
- Interactive charts:
  - Allocation pie chart
  - Gain/Loss bar chart
  - Price comparison line chart
  - Sentiment scatter chart
- Manage Holdings (CRUD): **add**, **update**, **delete**
- Auto-refresh dashboard every **5 seconds**
- Backend supports portfolio operations using either **symbol** (e.g. `BTC`) or numeric **id** (e.g. `11`) on `/api/portfolio/{symbol_or_id}`

---

## Screenshots

Add screenshots to a folder like `docs/screenshots/` and link them here.

Example:
- `docs/screenshots/dashboard.png`
- `docs/screenshots/manage-holdings.png`

---

## Tech stack

**Backend**
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic

**Frontend**
- Dash
- Plotly
- dash-bootstrap-components

**Database**
- SQLite (default)
- Optional PostgreSQL via `DATABASE_URL`

---

## Repository structure

```
.
 backend/
    app.py               # FastAPI app + routes
    crud.py              # DB operations
    database.py          # DB engine/session
    models.py            # SQLAlchemy models
    schemas.py           # Pydantic schemas
    requirements.txt
 frontend/
    app.py               # Dash UI
    requirements.txt
    assets/
        styles.css       # small UI polish
 data/
    sample_data.py        # seeds 50+ holdings + sentiment
 run_local.py              # starts backend + frontend together
 crypto_portfolio.db       # created automatically after first run
```

---

## Getting started

### Prerequisites

- Python **3.10+**
- pip

> Tip: If youre on a very new Python version and you see package install issues, use Python 3.11/3.12 for the smoothest dependency support.

### 1) Create a virtual environment

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

### 2) Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
.\.venv\Scripts\python.exe -m pip install -r .\frontend\requirements.txt
```

---

## Run the project

### Option A (recommended): start backend + frontend together

The launcher auto-selects free ports (helpful on Windows when a port is already in use):

```powershell
py .\run_local.py
```

It prints URLs like:
- Backend: `http://127.0.0.1:8000/api/health`
- Frontend: `http://127.0.0.1:8051/`

### Option B: run each service manually

**Backend**

```powershell
$env:BACKEND_HOST = "127.0.0.1"
$env:BACKEND_PORT = "8000"
py .\backend\app.py
```

**Frontend**

```powershell
$env:API_URL = "http://127.0.0.1:8000/api"
$env:DASH_PORT = "8051"
py .\frontend\app.py
```

---

## Seed sample data (50+ records)

The seed script generates **50+ unique portfolio holdings** and sentiment data.

1) Start the backend first.

2) Seed the database:

```powershell
$env:API_URL = "http://127.0.0.1:8000/api"
py .\data\sample_data.py
```

Notes:
- `crypto_symbol` is unique, so re-running the seed script will **skip** already-existing symbols.

---

## API documentation

Once the backend is running:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## API reference (summary)

Base path: `/api`

### Health
- `GET /api/health`

### Portfolio
- `GET /api/portfolio`
- `POST /api/portfolio`
- `GET /api/portfolio/{symbol_or_id}`
- `PUT /api/portfolio/{symbol_or_id}`
- `DELETE /api/portfolio/{symbol_or_id}`

### Sentiment
- `GET /api/sentiment`
- `POST /api/sentiment`

### Transactions
- `GET /api/transactions` (optional query: `?symbol=BTC`)
- `POST /api/transactions`

Example (PowerShell):

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/api/portfolio"
```

---

## Configuration

### Backend environment variables

- `DATABASE_URL`
  - Default: `sqlite:///./crypto_portfolio.db`
  - Example (Postgres): `postgresql+psycopg2://user:pass@localhost:5432/crypto`
- `BACKEND_HOST` (default: `127.0.0.1`)
- `BACKEND_PORT` (default: `8000`)

### Frontend environment variables

- `API_URL` (default: `http://127.0.0.1:8000/api`)
- `DASH_PORT` (default: `8051`)

---

## Troubleshooting

### Port already in use (WinError 10048)
- Use the launcher: `py .\run_local.py` (auto-picks ports)

### Frontend cant reach backend
- Confirm `API_URL` matches the backend port printed by the launcher.

### Old UI appears in the browser
- Stop all running Python processes, then restart `run_local.py`.
- Hard refresh the browser (Ctrl+F5).

### Reset database

If you want a fresh start:
- Stop the backend/frontend
- Delete `crypto_portfolio.db`
- Start again and re-seed data

---

## Contributing

- Keep changes focused
- If you update routes, env vars, or seed format, also update this README

---

## License

Add a license if you plan to publish publicly (MIT is a common choice).l postgresql-contrib

# macOS
brew install postgresql