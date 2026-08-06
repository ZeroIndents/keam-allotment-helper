# Setup & Deployment

Covers: local development, building the database, and production deployment
(nginx + gunicorn + systemd).

---

## 1. Local development

```bash
# 1. Clone + venv
git clone <your-repo-url> keam-helper
cd keam-helper
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 2. Build the database from official CEE allotment PDFs
#    (the ~120 MB colleges_v2.db is intentionally NOT in the repo — it is
#    generated data with student PII)
./venv/bin/python offline_parser.py pdf_source/2026_Phase3.pdf

# 3. Run
export DB_PATH="$(pwd)/colleges_v2.db"
./venv/bin/python app.py        # dev server on 127.0.0.1:5001
# or via gunicorn:
./venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
```

Open <http://127.0.0.1:5000>.

> Dev note: `python app.py` binds to `127.0.0.1:5001` with debug enabled only
> when `FLASK_DEBUG=1` is set. It is never exposed to the internet.

## 2. Environment variables

| Variable      | Purpose                           | Default                              |
|---------------|-----------------------------------|--------------------------------------|
| `DB_PATH`     | SQLite database path              | `./colleges_v2.db` (next to `app.py`)|
| `SECRET_KEY`  | Flask session signing key         | random per boot (sessions reset)     |
| `FLASK_DEBUG` | Set `1` for the dev debug server  | off                                  |

## 3. Building / refreshing the database

The database is produced from **official CEE Kerala allotment PDFs** dropped in
`pdf_source/`:

```bash
# Single file
./venv/bin/python offline_parser.py pdf_source/2026_Phase3.pdf

# All PDFs in pdf_source/
./venv/bin/python offline_parser.py --all
```

The parser auto-detects the document type (digital table, flowing text, or
scanned/OCR), rebuilds the header from the PDF's own ruling lines, and
normalizes college/course codes via the `KEAM_COLLEGES` / `KEAM_COURSES` maps
in `app.py`. See `docs/DATA_PIPELINE.md`.

**Ordering matters** for multi-phase years: import Phase 1 → Phase 2 → Phase 3
so later phases overwrite earlier duplicates (dedup keys on
`year + phase + appl_no`).

## 4. Production deployment (nginx + gunicorn + systemd)

Assumes Ubuntu/Debian, Python 3.12, and that the app lives at
`/var/www/college_project`.

### 4.1 App user + permissions

```bash
# Run as an unprivileged user (www-data here), NOT root
chown -R www-data:www-data /var/www/college_project
```

### 4.2 systemd unit — `/etc/systemd/system/college.service`

```ini
[Unit]
Description=KEAM Allotment Helper / Predictor (Flask + Gunicorn)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/college_project
EnvironmentFile=/etc/college.env
ExecStart=/var/www/college_project/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now college
systemctl status college
```

### 4.3 Environment file — `/etc/college.env` (chmod 600, root-only)

```bash
SECRET_KEY=<random 64 hex chars>
DB_PATH=/var/lib/college_project/colleges_v2.db
FLASK_DEBUG=0
```

```bash
sudo chmod 600 /etc/college.env
```

### 4.4 Nginx site — `/etc/nginx/sites-available/college`

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/college /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Add TLS (e.g. certbot) in front. This site is additionally exposed through a
**Cloudflare Tunnel**, which is what sets the `CF-Connecting-IP` and `Cf-Ray`
headers the app trusts for real client IPs.

## 5. Backups

`sqlite3 .backup` is safe to run against a live database (no locking issues).

```bash
# /usr/local/sbin/college_db_backup.sh — nightly 3:15 AM, keeps last 14
#!/usr/bin/env bash
set -euo pipefail
mkdir -p /var/backups/college
ts=$(date +%Y%m%d-%H%M)
/usr/bin/sqlite3 /var/lib/college_project/colleges_v2.db \
  ".backup '/var/backups/college/colleges_v2_${ts}.db'"
find /var/backups/college -name 'colleges_v2_*.db' -mtime +14 -delete
```

Cron: `/etc/cron.d/college-backup`

```
15 3 * * * root /usr/local/sbin/college_db_backup.sh
```

## 6. Common operations

| Task | Command |
|------|---------|
| Restart the app | `systemctl restart college` |
| Tail logs | `journalctl -u college -f` |
| Verify it's up | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/` |
| Rebuild DB from PDFs | `./venv/bin/python offline_parser.py pdf_source/2026_Phase3.pdf` |
| Dependency audit | `./venv/bin/pip-audit` |
