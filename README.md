<div align="center">

# 🎓 KEAM Allotment Helper

### Searchable archive of official CEE Kerala engineering allotment data with intelligent predictions

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)](#license)
[![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge)](https://gavinjoseph.in/keam)

<br/>

**290,000+** allotment rows · **142** colleges · **3** years of data · **Live at [gavinjoseph.in](https://gavinjoseph.in/keam)**

</div>

---

## 📸 Screenshots

<div align="center">

### 🔍 Allotment Finder
> Search across 290K+ official allotment rows with filters for year, phase, college, course, category, seat type, rank, and register number.

![Allotment Finder](https://via.placeholder.com/1200x600/0a0520/7c3aed?text=Allotment+Finder+%E2%80%94+Search+290K%2B+rows)

### 📊 Statistics Dashboard
> Interactive charts showing cutoff trends, category spreads, college comparisons, and migration tracking with D3-powered route maps.

![Statistics Dashboard](https://via.placeholder.com/1200x600/0a0520/7c3aed?text=Statistics+Dashboard+%E2%80%94+Charts+%26+Analytics)

### 🎯 Rank Predictor
> 5:3:2 board-normalization calculator with estimated merit-rank brackets based on official CEE formulas.

![Rank Predictor](https://via.placeholder.com/1200x600/0a0520/7c3aed?text=Rank+Predictor+%E2%80%94+5%3A3%3A2+Normalization)

### ⚡ Find My Options
> Enter your rank and instantly see which colleges and courses are within reach — tagged Safe, Moderate, or Ambitious.

![Find My Options](https://via.placeholder.com/1200x600/0a0520/7c3aed?text=Find+My+Options+%E2%80%94+Safe%2FModerate%2FAmbitious)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Allotment Finder** | Server-side DataTable over 290K+ rows. Filter by year, phase, college, course, category, seat type, rank, or register number. |
| 📊 **Statistics Dashboard** | KPIs, cutoff trends, category spreads, college×course heatmap, migration tracker with route maps. |
| 🎯 **Rank Predictor** | 5:3:2 board-normalization calculator (Math 50%, Physics 30%, Chemistry 20%) with estimated merit-rank brackets. |
| ⚡ **Find My Options** | Enter your rank → get Safe / Moderate / Ambitious college suggestions based on closing ranks. |
| 🔄 **Migration Tracker** | See how students switch colleges between allotment rounds (Phase 1 → 2 → 3). |
| 📄 **Document Toolkit** | Client-side photo/signature resizing, image→PDF, and PDF compression (no server upload). |
| 🗺️ **Cutoff Heatmap** | College × course heatmap showing opening vs closing ranks across phases. |
| ⚔️ **College Comparator** | Side-by-side comparison of two colleges' cutoffs across all branches. |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│              Browser (client)                 │
│  Bootstrap 5 · jQuery · DataTables ·          │
│  Chart.js · D3 · Tom Select · pdf.js          │
└──────────────────┬───────────────────────────┘
                   │ HTTPS (Cloudflare Tunnel)
┌──────────────────▼───────────────────────────┐
│              Nginx (reverse proxy)            │
│            → 127.0.0.1:5000                   │
└──────────────────┬───────────────────────────┘
┌──────────────────▼───────────────────────────┐
│        Gunicorn (3 workers) → Flask app       │
│                 app.py                        │
│  UI routes · JSON APIs · rate limiting        │
└──────────────────┬───────────────────────────┘
                   │ sqlite3
┌──────────────────▼───────────────────────────┐
│      SQLite DB — colleges_v2.db               │
│  table: colleges (290k+ allotment rows)       │
└──────────────────┬───────────────────────────┘
                   ▲
┌──────────────────┴───────────────────────────┐
│  offline_parser.py (build/maintain DB)        │
│  ← official CEE allotment PDFs (pdf_source/)  │
└──────────────────────────────────────────────┘
```

### Process Model

- **Gunicorn** runs 3 workers, all serving the same Flask app
- **SQLite** is the single source of truth (read-only from the app's point of view)
- **Rate limiting** is DB-backed, shared across all workers (300 req/min per IP)
- **Security headers** on every response: CSP, HSTS, X-Frame-Options, nosniff

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip
- (Optional) Tesseract OCR + Poppler for scanned PDFs

### Installation

```bash
# Clone the repository
git clone https://github.com/ZeroIndents/keam-allotment-helper-predictor.git
cd keam-allotment-helper-predictor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Building the Database

```bash
# Drop official CEE allotment PDFs into pdf_source/ and run:
python offline_parser.py
```

The parser auto-detects each PDF's layout (digital table, flowing text, or scanned/OCR) and imports all PDFs found in `pdf_source/`.

### Running the App

```bash
# Set the database path
export DB_PATH=/path/to/colleges_v2.db

# Run with Flask (development)
python app.py

# Or run with Gunicorn (production)
gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📡 API Reference

All endpoints are `GET`, return `application/json`, and are **read-only**.
Every `/api/*` and `/data` request is rate-limited per client IP (300 req/min).

### Search & Allotment Data

#### `GET /data` — DataTables server-side endpoint

| Param | Type | Meaning |
|-------|------|---------|
| `draw` | int | DataTables draw counter (echoed back) |
| `start` | int | Row offset (capped at 10,000,000) |
| `length` | int | Page size (clamped 1–1000) |
| `year` | int | Filter by year |
| `phase` | str | Comma-separated phases (`Phase1,Phase2,Phase3`) |
| `college` | str | Exact `college_name` |
| `course` | str | Exact `course_name` |
| `category` | str | Comma-separated category codes |
| `seat` | str | Seat-type substring (usually `SM`) |
| `rank` | int | Exact rank |
| `reg_no` | str | Register number or application number |

### Statistics Dashboard

| Endpoint | Returns |
|----------|---------|
| `GET /api/stats/kpi` | `{total_colleges, total_courses, lowest_cutoff, last_cutoff, top_branch}` |
| `GET /api/stats/top-colleges?course=` | Top-10 colleges by lowest SM cutoff |
| `GET /api/stats/rank-bands?year=&college=` | Seat counts per seat type |
| `GET /api/stats/phase-trends?year=&college=` | Phase-wise cutoff for top 8 courses |
| `GET /api/stats/category-spread?year=&college=` | Best/avg/worst rank per category |
| `GET /api/stats/college-cutoffs?college=` | Branch-wise cutoffs for a college |
| `GET /api/stats/top-branches?year=&college=` | Top-15 branches by lowest SM cutoff |
| `GET /api/stats/cutoff-matrix?year=&phase=&seat=` | Per college×course cutoff data |

### Dropdown Fillers

| Endpoint | Returns |
|----------|---------|
| `GET /api/years` | `[2026, 2025, ...]` distinct years |
| `GET /api/categories` | Sorted distinct category codes |
| `GET /api/colleges?course=` | Distinct college names |
| `GET /api/courses?college=` | Distinct course names |

### Cutoffs & Analytics

| Endpoint | Returns |
|----------|---------|
| `GET /api/rank-summary?college=&course=&year=` | Rank range per category |
| `GET /api/trends?college=&course=` | Year-over-year cutoff trends |
| `GET /api/options?rank=&year=&category=` | Safe/Moderate/Ambitious options |
| `GET /api/migrations?year=&from_phase=&to_phase=` | Students who switched colleges |

### Errors

- `400` — Missing/invalid required parameters
- `429` — Rate limit exceeded (`{"error": "rate_limited"}`)
- `500` — Internal error (safe empty payload, no stack traces)

---

## 📂 Data Pipeline — CEE PDF → SQLite

```
pdf_source/*.pdf
      │
      ▼
offline_parser.py ──► SQLite (colleges_v2.db)
      │                    table: colleges (~290,000 rows)
      │
      ├─ detect_format()              sniff page-1 header keywords
      ├─ build_header_column_map()    rebuild column layout from PDF ruling lines
      ├─ parse_allotment_list_pdf()   digital table path
      ├─ parse_allotment_list_text_fallback()  flowing-text path
      └─ parse_*_ocr()                scanned-image path (tesseract)
```

### How Format-Flexibility Works

CEE **changes the PDF layout every year** — sometimes between phases. The parser handles this by:

1. **Detecting the document kind** by sniffing keywords on page 1
2. **Reading ruling lines** via pdfplumber and rebuilding the header from the PDF's own column layout
3. **Falling back to regex** for flowing text without ruling lines
4. **OCR fallback** for scanned PDFs via Tesseract

### Database Schema

```sql
CREATE TABLE colleges (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    year                INTEGER,
    phase               TEXT,
    appl_no             TEXT,
    register_number     TEXT,
    rank                INTEGER,
    candidate_category  TEXT,
    college_name        TEXT,
    course_name         TEXT,
    seat_type           TEXT,
    sl_no               TEXT
);

CREATE INDEX idx_fast_matrix ON colleges(year, phase, candidate_category, college_name, course_name, rank);
CREATE INDEX idx_fast_line   ON colleges(year, phase, appl_no, college_name, course_name);
CREATE INDEX idx_fast_year_rank ON colleges(year, rank);
CREATE INDEX idx_fast_rank      ON colleges(rank);
CREATE INDEX idx_fast_reg       ON colleges(register_number);
CREATE INDEX idx_fast_appl      ON colleges(appl_no);
```

---

## 🎓 The KEAM Process

### What is KEAM?

**KEAM** (Kerala Engineering, Agriculture and Medical) is the state-level entrance examination conducted by the **Commissioner for Entrance Examinations (CEE), Government of Kerala**.

### Rank Preparation — 50:50 Model

| Component | Weight | Scaled to |
|-----------|--------|-----------|
| Normalized KEAM entrance (CBT) score | 50% | **300 marks** |
| Normalized Class 12 board score | 50% | **300 marks** |
| **Total KEAM index** | 100% | **600 marks** |

### 5:3:2 Board-Mark Normalization

| Subject | Weight | Scaled to |
|---------|--------|-----------|
| **Mathematics** | 50% | **150 marks** |
| **Physics** | 30% | **90 marks** |
| **Chemistry** | 20% | **60 marks** |

### Reservation Categories

| Code | Category | % of quota |
|------|----------|-----------|
| **SM** | State Merit (open) | 50% |
| **SEBC** | Socially & Educationally Backward Classes | 30% |
| **SC** | Scheduled Castes | 8% |
| **ST** | Scheduled Tribes | 2% |
| **EWS** | Economically Weaker Sections | as per norms |

---

## 🛡️ Security

- ✅ All SQL uses **parameterized queries** (no string interpolation)
- ✅ **Rate limiting** per client IP (DB-backed, shared across workers)
- ✅ **Security headers** on every response: CSP, HSTS, X-Frame-Options, nosniff
- ✅ **Fail-open** design — rate limit bookkeeping never breaks the public site
- ✅ Real client IP via `CF-Connecting-IP` header (only trusted with `Cf-Ray` present)

---

## 📁 Project Structure

```
.
├── app.py                      # Flask application (UI + API routes)
├── offline_parser.py           # PDF → SQLite parser (format-flexible)
├── offline_parser_working.py   # Working copy of the parser
├── requirements.txt            # Python dependencies
├── colleges_v2.db              # SQLite database (not in repo)
├── pdf_source/                 # Official CEE allotment PDFs
├── static/                     # Static assets (CSS, JS)
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Allotment Finder (main page)
│   ├── statistics.html         # Statistics Dashboard
│   ├── predictor.html          # Rank Predictor
│   ├── options.html            # Find My Options
│   ├── resizer.html            # Document Toolkit
│   ├── counselling.html        # Counselling Guide
│   └── guide.html              # How to Use Guide
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── API.md                  # API reference
│   ├── DATA_PIPELINE.md        # PDF parsing pipeline
│   ├── KEAM_GUIDE.md           # KEAM process deep dive
│   └── SETUP.md                # Setup & deployment
└── tailwind.config.js          # Tailwind CSS config (statistics page)
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask 3, Gunicorn |
| **Database** | SQLite (read-only, ~120MB) |
| **Frontend** | Bootstrap 5, jQuery, DataTables, Chart.js, D3.js, Tom Select |
| **PDF Parsing** | pdfplumber, pypdf, pdf2image, pytesseract |
| **Deployment** | Nginx, Cloudflare Tunnel, systemd |
| **Styling** | Tailwind CSS (statistics page) |

---

## 📄 License

Private repository — all rights reserved.

---

<div align="center">

**Built with ❤️ by [Gavin Joseph](https://gavinjoseph.in)**

[![GitHub](https://img.shields.io/badge/GitHub-ZeroIndents-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ZeroIndents)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Gavin%20Joseph-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gavin-joseph-792a433a8/)
[![Instagram](https://img.shields.io/badge/Instagram-gavin._.joseph-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/gavin._.joseph/)

</div>
