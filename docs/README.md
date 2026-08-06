# Documentation

| Doc | What it covers |
|-----|----------------|
| [KEAM_GUIDE.md](KEAM_GUIDE.md) | Deep guide to the real KEAM process: 50:50 rank model, the 5:3:2 board normalization, allotment phases, reservation categories, seat types, code glossary. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture: request lifecycle, pages, API surface, shared rate limiting, deployment topology. |
| [SETUP.md](SETUP.md) | Local development, environment variables, DB build, production deployment (systemd + nginx), backups, common ops. |
| [DATA_PIPELINE.md](DATA_PIPELINE.md) | How official CEE allotment PDFs become the SQLite database: format detection, header reconstruction, OCR fallback, schema, dedup. |
| [API.md](API.md) | Reference for every public JSON endpoint: params, shapes, and error codes. |

**Quick start:** see [SETUP.md](SETUP.md) §1 for local dev and §4 for
production.
