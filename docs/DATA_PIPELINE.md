# Data Pipeline — CEE PDF → SQLite

How official KEAM allotment PDFs become the searchable table behind the site.

```
pdf_source/*.pdf
      │
      ▼
offline_parser.py ──► SQLite (colleges_v2.db)
      │                    table: colleges (~290,000 rows)
      │
      ├─ detect_format()      sniff page-1 header keywords
      ├─ build_header_column_map()   rebuild column layout from the PDF's
      │                        own ruling lines (pdfplumber)
      ├─ parse_allotment_list_pdf()  digital table path
      ├─ parse_allotment_list_text_fallback()   flowing-text path
      └─ parse_*_ocr()        scanned-image path (tesseract)
```

## The problem this solves

CEE **changes the PDF layout every year** — sometimes between phases. Column
order, header wording, and even row grouping vary. A hard-coded positional
parser would break every cycle. The parser is therefore **format-flexible**:

1. **Detect the document kind** (`detect_format`) by sniffing keywords on
   page 1 — *allotment list*, *cutoff matrix*, or *scanned image* (no text
   layer).
2. **Digital table with ruling lines** — `pdfplumber` reads the vector ruling
   lines, then `build_header_column_map()` reconstructs which column is which
   from the header row(s), matching against a `HEADER_SYNONYMS` dictionary
   (e.g. "Application No", "Appl. No", "APPLNO" → `appl_no`). New header
   spellings go into that dictionary, not into parsing logic.
3. **Flowing text (no ruling lines)** — a regex line-grouping parser looks for
   a row-start pattern (`SlNo, ApplNo, Rank, Category, ...`) and reassembles
   wrapped lines.
4. **Scanned PDFs** — pages are rendered (`pdf2image` + `poppler-utils`) and
   OCR'd (`tesseract`), with auto-rotation for skewed pages.

To support a genuinely new layout in future, add one `detect_*`/`parse_*`
function pair and register it in `FORMAT_HANDLERS` — dictionaries, DB schema,
and dedup logic stay untouched.

## Normalization

- `resolve_college(raw)` / `resolve_course(raw)` map CEE's short codes to
  canonical `CODE - Full Name` strings using `KEAM_COLLEGES` / `KEAM_COURSES`
  (kept in sync with `app.py`).
- `extract_seat_type(tail)` pulls the quota type (`SM`, …) out of the row tail.
- `_clean_cell` strips stray whitespace/control chars.
- Year + phase are parsed from the filename (`2026_Phase3.pdf` → 2026, Phase3)
  and cross-checked against page text.

## Database schema

```sql
CREATE TABLE colleges (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    year                INTEGER,          -- 2024, 2025, 2026 ...
    phase               TEXT,             -- Phase1 | Phase2 | Phase3
    appl_no             TEXT,             -- application number
    register_number     TEXT,             -- registration number
    rank                INTEGER,          -- KEAM merit rank
    candidate_category  TEXT,             -- SM, EZ, MU, SC, ST ...
    college_name        TEXT,             -- "TVE - College of Engineering, ..."
    course_name         TEXT,             -- "CS - Computer Science & Engineering"
    seat_type           TEXT,             -- quota type, usually SM
    sl_no               TEXT              -- row number from the PDF
);

CREATE INDEX idx_fast_matrix ON colleges(year, phase, candidate_category, college_name, course_name, rank);
CREATE INDEX idx_fast_line   ON colleges(year, phase, appl_no, college_name, course_name);
```

The two indexes cover the hot query shapes: the statistics drill-downs
(`year/phase/category/college/course/rank`) and the DataTables `/data` filters
(`year/phase/appl_no/college/course`).

## Dedup & ordering

- Rows are keyed on `year + phase + appl_no`; later imports overwrite earlier
  duplicates (`INSERT OR REPLACE` semantics via the parser's upsert).
- **Import phases in order** (Phase1 → Phase2 → Phase3) so the final table
  always reflects the latest phase list per candidate.

## App-side read path

`app.py` opens a fresh `sqlite3` connection per request (`row_factory =
sqlite3.Row`), runs fully parameterized queries, and closes it in a `finally`.
There is no write path in the running web app — the DB is a build artifact.
