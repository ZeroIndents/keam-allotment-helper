# Architecture

How the application is put together, what each piece does, and how data flows
through it.

```
                        ┌──────────────────────────────────────────┐
                        │              Browser (client)             │
                        │  Bootstrap 5 · jQuery · DataTables ·      │
                        │  Chart.js · D3 · Tom Select · pdf.js      │
                        └───────────────────┬──────────────────────┘
                                            │ HTTPS (Cloudflare Tunnel)
                        ┌───────────────────▼──────────────────────┐
                        │              Nginx (reverse proxy)        │
                        │            → 127.0.0.1:5000               │
                        └───────────────────┬──────────────────────┘
                        ┌───────────────────▼──────────────────────┐
                        │        Gunicorn (3 workers) → Flask app   │
                        │                 app.py                    │
                        │  UI routes · JSON APIs · rate limiting    │
                        └───────────────────┬──────────────────────┘
                                            │ sqlite3
                        ┌───────────────────▼──────────────────────┐
                        │      SQLite DB — colleges_v2.db           │
                        │  table: colleges (290k+ allotment rows)   │
                        └───────────────────┬──────────────────────┘
                                            ▲
                        ┌───────────────────┴──────────────────────┐
                        │  offline_parser.py (build/maintain DB)    │
                        │  ← official CEE allotment PDFs (pdf_source/)│
                        └──────────────────────────────────────────┘
```

## Process model

- **Gunicorn** runs 3 workers, all serving the same Flask app.
- **SQLite** is the single source of truth. Because SQLite allows one writer at
  a time, the app keeps connections short-lived (`get_db_connection()` per
  request, closed in `finally`), uses the built-in indexes
  (`idx_fast_matrix`, `idx_fast_line`), and rate-limit bookkeeping is done in
  `BEGIN IMMEDIATE` transactions (see below).
- The database is **read-only from the app's point of view** — it is written
  only by `offline_parser.py` during a data import. No write path exists in the
  running web app.

## Request lifecycle

1. Request arrives via Cloudflare Tunnel → nginx → gunicorn worker → Flask.
2. `before_request` (`global_api_rate_limit`) — every call to `/data` or
   `/api/*` is checked against a **DB-backed per-client-IP rate limit**
   (300 req/min, atomic `BEGIN IMMEDIATE` check-and-insert so all 3 workers
   share one accurate counter). Over-limit calls get `429`.
3. Route handler runs; every SQL statement is **parameterized** (no string
   interpolation of user input).
4. `after_request` (`add_security_headers`) stamps every response with:
   - `Content-Security-Policy` (self + pinned CDNs, `frame-ancestors 'none'`),
   - `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
   - `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy`.

## The client IP problem

Behind nginx, `request.remote_addr` is always `127.0.0.1`. The app therefore
reads the real visitor IP from the `CF-Connecting-IP` header set by
cloudflared — but **only trusts it when a `Cf-Ray` header is present**
(a Cloudflare marker). Without `Cf-Ray`, the header is treated as spoofable and
ignored. This matters for the rate limiter.

## Pages (server-rendered shells + client-side data)

| Route | Page | What it does |
|-------|------|--------------|
| `/` | Allotment Finder | Server-side DataTable over the whole DB. Filters: year, phase (multi), college, course, category (multi), seat type, rank, register/appl no. |
| `/predictor` | Rank Predictor | 5:3:2 board-normalization calculator (see `docs/KEAM_GUIDE.md` §3) with estimated merit-rank brackets. All computation is client-side. |
| `/statistics` | Statistics Dashboard | KPIs, cutoff trends, category spreads, phase trends, college×course heatmap, migration tracker. Pulls data from `/api/stats/*`. |
| `/resizer` | Document Toolkit | Client-side photo/signature resizing, image→PDF, PDF compression. Nothing is uploaded to the server (works in the browser via canvas / pdf.js). |
| `/trends` | — | Legacy URL, 302-redirects to `/statistics`. |
| `/sitemap.xml` | — | Static sitemap served from disk. |

## API surface

All data endpoints are JSON and read-only. Full reference in
`docs/API.md`. Key ones:

- `GET /data` — DataTables server-side endpoint (draw/start/length + filters).
- `GET /api/stats/*` — 8 endpoints powering the statistics dashboard
  (kpi, top-colleges, rank-bands, phase-trends, category-spread,
  college-cutoffs, top-branches, cutoff-matrix).
- `GET /api/advanced-stats` — multi-select drill-down for one college.
- `GET /api/years|categories|colleges|courses` — dropdown fillers.
- `GET /api/rank-summary` — category rank ranges for a college+course.
- `GET /api/trends` — year-over-year cutoff trends per category.
- `GET /api/migrations` — candidates who *jumped* colleges/courses between
  two phases (self-join on `appl_no`).

## Rate limiting (shared across workers)

The naive approach — an in-memory dict per process — breaks with multiple
gunicorn workers (each worker has its own counter). The fix: the limiter lives
**in SQLite**, keyed by `api:<ip>`, with a one-hour sliding window (counts
requests in the last 60s). The check-and-insert runs inside `BEGIN IMMEDIATE`
so concurrent workers see an accurate count instead of racing. If the DB is
unavailable the limiter *fails open* — the public site must never go down
because rate-limit bookkeeping broke.

## Dependencies

- **Backend:** Python 3.12, Flask, Gunicorn, `pypdf` (parser). Everything else
  is the standard library.
- **Frontend (CDN):** Bootstrap 5, jQuery, DataTables, Tom Select, Chart.js,
  D3, pdf.js. The CSP pins these CDN origins.
- **Parsing (offline only):** `pdfplumber`, `pdf2image`, `pytesseract`,
  `poppler-utils`, `tesseract-ocr` — see `docs/DATA_PIPELINE.md`.
