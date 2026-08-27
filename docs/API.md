# API Reference

All endpoints are `GET`, return `application/json`, and are **read-only**.
Every `/api/*` and `/data` request is rate-limited per client IP (300
req/min shared budget; excess returns `429 {"error": "rate_limited"}`).

Base URL: `https://<your-domain>` (or `http://127.0.0.1:5000` locally).

---

## Search & allotment data

### `GET /data` — DataTables server-side endpoint

Query params:

| Param | Type | Meaning |
|-------|------|---------|
| `draw` | int | DataTables draw counter (echoed back) |
| `start` | int | Row offset (capped at 10,000,000) |
| `length` | int | Page size (clamped 1–1000) |
| `year` | int | Filter by year |
| `phase` | str | Comma-separated phases, e.g. `Phase1,Phase2`. Omit to get only real phases. `ProvisionalPhase1` matches provisional lists too. |
| `college` | str | Exact `college_name` |
| `course` | str | Exact `course_name` |
| `category` | str | Comma-separated category codes, case-insensitive substring match |
| `seat` | str | Seat-type substring (usually `SM`) |
| `rank` | int | Exact rank |
| `reg_no` | str | Register number **or** application number |

Response (DataTables shape):

```json
{
  "draw": 1,
  "recordsTotal": 292056,
  "recordsFiltered": 8421,
  "data": [
    {
      "year": 2026,
      "phase": "Phase3",
      "register_number": "1146248",
      "rank": 60,
      "college_name": "TVE - College of Engineering, Thiruvananthapuram",
      "course_name": "CS - Computer Science & Engineering",
      "candidate_category": "SM",
      "seat_type": "SM"
    }
  ]
}
```

---

## Statistics dashboard

All accept optional `year` (and some `college` / `course` / `phase` / `seat`)
query params.

| Endpoint | Returns |
|----------|---------|
| `GET /api/stats/kpi` | `{total_colleges, total_courses, lowest_cutoff, last_cutoff, top_branch}` |
| `GET /api/stats/top-colleges?course=` | Top-10 colleges by lowest SM cutoff for a course: `[{college, cutoff, last}]` |
| `GET /api/stats/rank-bands?year=&college=` | Seat counts per seat type: `[{band, seats}]` |
| `GET /api/stats/phase-trends?year=&college=` | Phase-wise cutoff for top 8 courses: `{phases[], courses[], data{phase→course→rank}}` |
| `GET /api/stats/category-spread?year=&college=` | Best/avg/worst rank per category: `{CAT: {best, avg, worst}}` |
| `GET /api/stats/college-cutoffs?college=` | Branch-wise `{course, lowest, last, seats}` for a college (400 if no college) |
| `GET /api/stats/top-branches?year=&college=` | Top-15 branches by lowest SM cutoff: `[{course, cutoff, last}]` |
| `GET /api/stats/cutoff-matrix?year=&phase=&seat=` | Per college×course `{college, course, lowest, last, seats}` (heatmap source) |

### `GET /api/stats`

```json
{ "total_rows": 292056, "unique_colleges": 142, "total_years": 3 }
```

### `GET /api/advanced-stats?college=...`

Multi-select drill-down for a single college:

| Param | Meaning |
|-------|---------|
| `college` | **required**, exact college name |
| `courses[]` | repeatable, course names |
| `years[]` | repeatable, years (default `2026`) |
| `phases[]` | repeatable, phases (default `Phase1`) |
| `categories[]` | repeatable, category codes (default `GN,SM`) |
| `seats[]` | repeatable, seat types (default `SM`) |
| `max_rank` | int, cap on rank |

Response: `{years[], courses[], chart_series{year - cat → course→rank}, table_matrix[{year, phase, category, course, seat_type, cutoff, seats}]}`

---

## Dropdown fillers

| Endpoint | Returns |
|----------|---------|
| `GET /api/years` | `[2026, 2025, ...]` distinct years, desc |
| `GET /api/categories` | sorted distinct category codes |
| `GET /api/colleges?course=` | distinct college names (optionally filtered by course) |
| `GET /api/courses?college=` | distinct course names (optionally filtered by college) |

---

## Cutoffs & migration analytics

### `GET /api/rank-summary?college=&course=&year=`

Rank range per category for one college+course:

```json
[{"category": "SM", "start": 60, "end": 1334}, ...]
```

`400` if `college` or `course` missing.

### `GET /api/trends?college=&course=`

Year-over-year lowest cutoff per category:

```json
{ "SM": {2024: 182, 2025: 97, 2026: 60}, "EZ": {...} }
```

`400` if `college` or `course` missing.

### `GET /api/migrations?year=&from_phase=&to_phase=&college=&course=`

Candidates who changed college/course between two phases (self-join on
`appl_no`):

```json
{
  "total_migrations": 312,
  "migrations": [{"appl_no": "...", "rank": 60, "from_college": "...", "from_course": "...", "to_college": "...", "to_course": "...", "category": "SM", "seat_type": "SM"}],
  "top_destinations": [{"college": "...", "count": 44}],
  "top_sources": [{"college": "...", "count": 40}]
}
```

`year`, `from_phase`, `to_phase` are required (`400` otherwise); results capped
at 500 rows, ordered by rank.

---

## Misc

| Endpoint | Notes |
|----------|-------|
| `GET /` | Allotment Finder page |
| `GET /predictor` | Rank Predictor page (client-side calc) |
| `GET /statistics` | Statistics dashboard |
| `GET /resizer` | Document toolkit |
| `GET /trends` | 302 → `/statistics` |
| `GET /robots.txt` | Crawl rules + sitemap pointer |
| `GET /sitemap.xml` | XML sitemap (generated; lastmod = template mtime) |

## Errors

- `400` — missing/invalid required parameters.
- `429` — rate limit exceeded (`{"error": "rate_limited"}`).
- `500` — internal error (API endpoints return a safe empty/`internal_error`
  payload rather than stack traces).
