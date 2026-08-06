# KEAM Allotment Helper / Predictor

Searchable archive of official CEE Kerala (KEAM) engineering allotment data across
years and phases, plus a rank predictor, a statistics dashboard, and a browser-side
document toolkit — served live at [gavinjoseph.in](https://gavinjoseph.in).

## Features

- **Allotment Finder** (`/`) — server-side DataTable over 290k+ allotment rows.
  Filter by year, phase, college, course, category, seat type, rank, or register number.
- **Rank Predictor** (`/predictor`) — 2026 CEE 5:3:2 board-normalization calculator
  with estimated merit-rank brackets.
- **Statistics Dashboard** (`/statistics`) — cutoff trends, category spreads,
  college × course heatmap, and a migration (phase-jump) tracker with route map.
- **Document Toolkit** (`/resizer`) — client-side photo/signature resizing,
  image-to-PDF, and PDF compression (no uploads to the server).

## Tech stack

- Python 3.12 / Flask 3 / Gunicorn
- SQLite (the ~120 MB `colleges_v2.db` is *not* in the repo — rebuild it with
  `offline_parser.py` from the PDFs in `pdf_source/`)
- Nginx reverse proxy + Cloudflare Tunnel
- Bootstrap 5, jQuery, DataTables, Tom Select, Chart.js, D3, pdf.js (client-side)

## Setup

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

export DB_PATH=/path/to/colleges_v2.db
./venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
```

### Building the database

```bash
# Parse official CEE allotment PDFs into the SQLite DB:
./venv/bin/python offline_parser.py pdf_source/2026_Phase3.pdf
```

## Documentation

The full docs live in [`docs/`](docs/README.md):

- [Deep guide to the KEAM process](docs/KEAM_GUIDE.md) — the 50:50 rank model,
  5:3:2 board normalization, allotment phases, reservation categories.
- [Architecture](docs/ARCHITECTURE.md) — how the app is put together.
- [Setup & deployment](docs/SETUP.md) — local dev through production.
- [Data pipeline](docs/DATA_PIPELINE.md) — CEE PDF → SQLite.
- [API reference](docs/API.md) — every public endpoint.

## Security notes

- All SQL uses parameterized queries.
- Public `/data` and `/api/*` endpoints are rate-limited per client IP
  (DB-backed so it works across all gunicorn workers).
- Security headers on every response: CSP, HSTS, X-Frame-Options, nosniff,
  Referrer-Policy, Permissions-Policy.
- Run gunicorn as an unprivileged user; keep the DB outside the web root.
- Nightly online backups: `/usr/local/sbin/college_db_backup.sh` (keeps 14).

## License

Private repository — all rights reserved.
