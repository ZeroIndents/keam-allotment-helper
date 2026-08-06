from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from datetime import timedelta
import sqlite3
import os
import time
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=32 * 1024 * 1024,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'colleges_v2.db'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "pdf_source")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Master Alias Dictionaries
KEAM_COLLEGES = {
    "AAE": "Al-Azhar College of Engineering and Technology, Idukki", "AAP": "Al-Ameen Engineering College, Palakkad",
    "ADR": "College of Engineering, Adoor", "AEC": "College of Engineering of Aranmula, Pathanamthitta",
    "AIK": "Albertian Institute of Science and Technology, Kochi", "AJC": "Amal Jyothi College of Engineering, Kottayam",
    "AME": "Rajadhani Institute of Science and Technology, Palakkad", "ASI": "Adi Shankara Institute of Engineering and Technology, Ernakulam",
    "ATP": "Ahalia School of Engineering and Technology, Palakkad", "AWH": "AWH Engineering College, Kozhikkode",
    "BJK": "Bishop Jerome Institute, Kollam", "BMC": "Baselios Mathews II College of Engineering, Kollam",
    "CCE": "Christ College of Engineering, Thrissur", "CCV": "MGM Technological Campus, Valanchery",
    "CDI": "College of Dairy Science & Technology, Idukki", "CDP": "College of Dairy Science and Technology, Pookode",
    "CDT": "Verghese Kurien Institue of Dairy & Food Technology, Thrissur", "CDV": "College of Dairy Science and Technology, Thiruvananthapuram",
    "CEA": "College of Engineering, Attingal", "CEC": "College of Engineering, Cherthala",
    "CEK": "College of Engineering, Kottarakkara, Kollam", "CEM": "College of Engineering Muttathara, Thiruvananthapuram",
    "CEN": "College of Engineering and Technology, Payyanur", "CHN": "College of Engineering, Chengannoor",
    "CIM": "Mentor Academy for Design Entrepreneurship Innovation and Technology, Ernakulam", "CKC": "Christ Knowledge City, Ernakulam",
    "CMA": "Carmel College of Engineering and Technology, Alappuzha", "COU": "KUFOS, School of Ocean Engineering and Underwater Technology, Ernakulam",
    "DMC": "M. Dasan Institute of Technology, Kozhikode", "ECE": "ICCS College of Engineering and Management, Thrissur",
    "EKC": "Eranad Knowledge City Technical Campus, Malappuram", "FIT": "Federal Institute of Science and Technology, Ernakulam",
    "GIK": "Gregorian Institute of Technology, Kottayam", "HGW": "Holy Grace Academy of Engineering, Thrissur",
    "ICE": "Ilahia College of Engineering and Technology, Ernakulam", "IDK": "Government Engineering College, Idukki",
    "IES": "I E S College of Engineering, Thrissur", "IGW": "Indira Gandhi Institute of Engineering and Technology, Ernakulam",
    "JBT": "Jai Bharath College of Management and Engineering Technology, Ernakulam", "JCE": "Jawaharlal College of Engineering and Technology, Palakkad",
    "JEC": "Jyothi Engineering College, Thrissur", "JIT": "John Cox Memorial C S I Institute of Technology, Thiruvananthapuram",
    "KCT": "Kelappaji College of Agricultural Engineering and Food Technology, Tavanur", "KGR": "College of Engineering Kidangoor, Kottayam",
    "KIT": "Kottayam Institute of Technology and Science, Kottayam", "KKE": "Government Engineering College, Kozhikkode",
    "KMC": "KMCT College of Engineering, Kozhikode", "KME": "K M E A Engineering College, Cochin",
    "KMI": "KMCT Institute of Technology and Management, Malappuram", "KMT": "KMCT Institute of Emerging Technology and Management, Kozhikode",
    "KMV": "KMCT College of Technology", "KMW": "KMCT College of Engineering for Women, Kozhikode",
    "KMY": "KMCT Institute of Engineering", "KMZ": "KMCT College of Engineering",
    "KNP": "College of Engineering, Karunagappally, Kollam", "KNR": "Government College of Engineering, Kannur",
    "KSD": "LBS College of Engineering, Kasaragod", "KTE": "Government Rajiv Gandhi Institute of Technology, Kottayam",
    "KVE": "KVM College of Engineering and Information Technology, Alappuzha", "LBT": "LBS Institute of Technology for Women, Thiruvananthapuram",
    "LMC": "Lourdes Matha College of Science and Technology, Thiruvananthapuram", "MAC": "Mar Athanasius College of Engineering, Kothamangalam",
    "MBC": "Mar Baselios Christian College of Engineering and Technology, Idukki", "MBI": "Mar Baselios Institute of Technology and Science, Ernakulam",
    "MBT": "Mar Baselios College of Engineering and Technology, Thiruvananthapuram", "MCC": "Musaliar College Of Engineering, Thiruvananthapuram",
    "MCE": "Marian Engineering College, Thiruvananthapuram", "MCK": "Musaliar College of Engineering and Technology, Pathanamthitta",
    "MCT": "Mohandas College of Engineering and Technology, Thiruvananthapuram", "MDL": "Model Engineering College, Ernakulam",
    "MEA": "M E A Engineering College, Vengoor", "MEC": "Malabar College of Engineering and Technology, Thrissur",
    "MEE": "MES College of Engineering and Technology, Ernakulam", "MEK": "MES Institute of Technology and Management, Kollam",
    "MES": "M E S College of Engineering, Kuttippuram", "MET": "Mets School of Engineering, Thrissur",
    "MGC": "M G College of Engineering, Thiruvananthapuram", "MGE": "MGM College of Engineering & Technology, Ernakulam",
    "MGP": "Saintgits College of Engineering, Kottayam", "MHP": "ACE College Of Engineering, Thiruvananthapuram",
    "MLM": "Mangalam College of Engineering, Kottayam", "MLT": "Malabar Institute of Technology, Kannur",
    "MNR": "College of Engineering, Munnar", "MUS": "Muslim Association College of Engineering, Thiruvananthapuram",
    "MUT": "Muthoot Institute of Technology and Science, Ernakulam", "MZC": "Mount Zion College of Engineering, Pathanamthitta",
    "NCE": "Nehru College of Engineering and Research Centre, Thrissur", "NIE": "Nirmala College of Engineering Technology and Management, Thirissur",
    "NSS": "N S S College of Engineering, Palakkad", "PAA": "P A Aziz College of Engineering and Technology, Thiruvananthapuram",
    "PEC": "College of Engineering Pathanapuram, Kollam", "PJR": "College of Engineering Poonjar, Kottayam",
    "PKD": "Government Engineering College, Palakkad", "PRC": "Providence College of Engineering, Chengannur",
    "PRN": "College of Engineering Perumon, Kollam", "PRP": "College of Engineering and Management Punnnapra",
    "PTA": "College of Engineering, Kallooppara, Thiruvalla", "RCE": "Royal College of Engineering and Technology, Thrissur",
    "RET": "Rajagiri School of Engineering and Technology, Ernakulam", "RIE": "Rajadhani Institute of Engineering and Technology, Thiruvananthapuram",
    "SBC": "Sree Buddha College of Engineering, Alappuzha", "SCM": "SCMS School of Engineering and Technology, Ernakulam",
    "SCT": "S C T College of Engineering, Thiruvananthapuram", "SHR": "Sahrdaya College of Engineering and Technology, Thrissur",
    "SIT": "Sarabhai Institute of Science and Technology, Thiruvananthapuram", "SJC": "St Josephs College of Engineering and Technology, Palai",
    "SNC": "Sree Narayana Guru College of Engineering and Technology, Kannur", "SNG": "Sree Narayana Gurukulam College of Engineering, Ernakulam",
    "SNM": "SNM Institute of Management and Technology, Ernakulam", "SNP": "Sree Narayana Institute of Technology, Adoor",
    "SPT": "Sreepathy Institute of Management and Technology, Palakkad", "STC": "St Thomas Colllege of Engineering and Technology, Alappuzha",
    "STI": "St. Thomas Institute For Science and Technology, Thiruvananthapuram", "STM": "St.Thomas College of Engineering and Technology, Kannur",
    "TCE": "TOMS College of Engineering, Kottayam", "TCR": "Government Engineering College, Thrissur",
    "TCT": "Trinity College of Engineering, Thiruvananthapuram", "TEC": "Travancore Engineering College, Kollam",
    "TJE": "Thejus Engineering College, Thrissur", "TKI": "T K M Institute of Technology, Kollam",
    "TKM": "T K M College of Engineering, Kollam", "TKR": "College of Engineering, Trikaripur",
    "TLY": "College of Engineering, Thalassery, Kannur", "TOC": "Toc H Institute of Science and Technology, Ernakulam",
    "TRV": "Government Engineering College Barton Hill, Thiruvananthapuram", "TVE": "College of Engineering, Thiruvananthapuram",
    "UCC": "Institute of Engineering and Technology, Malappuram", "UCE": "University College of Engineering, Thodupuzha",
    "UCK": "University College of Engineering, Kariavattom, Thiruvananthapuram", "UKP": "UKF College of Engineering and Technology, Kollam",
    "UNT": "Universal Engineering College, Thrissur", "VAK": "Vidya Academy of Science and Technology, Thiruvananthapuram",
    "VAS": "Vidya Academy of Science and Technology, Thrissur", "VDA": "College of Engineering, Vadakara",
    "VIT": "VISAT Engineering College, Ernakulam", "VJC": "Viswajyothi College of Engineering and Technology, Ernakulam",
    "VKE": "Valia Koonambaikulathamma College of Engineering and Technology, Parippally", "VML": "Vimal Jyothi Engineering College, Kannur",
    "VPE": "Mahaguru Institute of Technology, Mavelikkara, Alappuzha", "VVT": "Veda Vyasa Institute of Technology, Malappuram",
    "WYD": "Government Engineering College, Wayanad", "YCE": "Younus College of Engineering and Technology, Kollam"
}

KEAM_COURSES = {
    "CS": "Computer Science & Engineering", "EC": "Electronics & Communication", "EE": "Electrical & Electronics",
    "ME": "Mechanical Engineering", "CE": "Civil Engineering", "AH": "Artificial Intelligence and Machine Learning",
    "AD": "Artificial Intelligence and Data Science", "CY": "Computer Science and Engineering (Cyber Security)",
    "BM": "Bio Medical Engineering", "AU": "Automobile Engineering", "CL": "Computer Science and Engineering (AI and ML)",
    "CO": "Computer Science & Engineering (Data Science)", "CT": "Computer Science & Engineering (Artificial Intelligence)",
    "CH": "Chemical Engineering", "MG": "Metallurgical and Materials Engineering", "FT": "Food Technology",
    "MA": "Mechanical (Automobile)", "EB": "Electronics & Biomedical Engg", "RB": "Robotics and Automation Engineering",
    "DS": "Dairy Technology", "AE": "Applied Electronics & Instrumentation", "CG": "Computer Science and Design",
    "CU": "Computer Science and Business Systems", "EI": "Electronics & Instrumentation", "FS": "Safety & Fire Engineering",
    "IN": "Internet of Things", "AO": "Aeronautical Engineering", "CK": "Civil Engineering with Computer",
    "MN": "Mechanical Engineering (Industry)", "MR": "Mechatronics Engineering", "BR": "Biomedical & Robotic Engineering",
    "AG": "B.Tech. (Agrl. Engg.)", "IT": "Information Technology", "ES": "Electronics and Computer Engineering",
    "BB": "Bio Technology and Biochemical Engineering", "EV": "Electronics Engineering (VLSI Design & Technology)",
    "IB": "Computer Science & Engineering (IoT & Cyber Security)", "PE": "Production Engineering", "CB": "Cyber Physical Systems",
    "PT": "Printing Technology", "EP": "Electronics and Computer Science", "PO": "Polymer Engg."
}

# AUTO-FORMAT SHORT CODES
KEAM_COLLEGES = {code: f"{code} - {name}" for code, name in KEAM_COLLEGES.items()}
KEAM_COURSES = {code: f"{code} - {name}" for code, name in KEAM_COURSES.items()}

# Only real allotment phases — no provisional/trial
STATS_PHASES = ('Phase1', 'Phase2', 'Phase3')
STATS_PHASE_SQL = "AND phase IN ('Phase1','Phase2','Phase3')"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- RATE LIMITING (shared across gunicorn workers, DB-backed) ---
def _client_ip():
    """Real client IP. Behind nginx/Cloudflare, remote_addr is always 127.0.0.1,
    so use the CF-Connecting-IP header set by cloudflared. Only trust it when a
    Cloudflare marker (Cf-Ray) is present — otherwise the header is trivially spoofable
    by anyone hitting the origin directly."""
    if request.headers.get('Cf-Ray'):
        return request.headers.get('CF-Connecting-IP') or request.remote_addr or 'unknown'
    return request.remote_addr or 'unknown'


def _rate_limit(bucket, limit):
    """DB-backed rate limit shared across gunicorn workers. Returns True if allowed.
    The check + insert run inside a BEGIN IMMEDIATE transaction so concurrent
    workers see an accurate count (no check/insert race)."""
    now = int(time.time())
    conn = None
    try:
        conn = get_db_connection()
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS api_rate (bucket TEXT, ts INTEGER)")
        cur.execute("DELETE FROM api_rate WHERE ts < ?", (now - 3600,))
        cur.execute("SELECT COUNT(*) FROM api_rate WHERE bucket = ? AND ts >= ?", (bucket, now - 60))
        if cur.fetchone()[0] >= limit:
            conn.rollback()
            return False
        cur.execute("INSERT INTO api_rate (bucket, ts) VALUES (?, ?)", (bucket, now))
        conn.commit()
        return True
    except Exception:
        # Rate-limit bookkeeping must never break the public site (fail open).
        try:
            conn.rollback()
        except Exception:
            pass
        return True
    finally:
        if conn:
            conn.close()


def _api_allowed(ip, limit):
    """Shared per-IP budget across all public data APIs."""
    return _rate_limit(f"api:{ip}", limit)


@app.before_request
def global_api_rate_limit():
    """Cap the public data APIs per client IP."""
    if request.path == '/data' or request.path.startswith('/api/'):
        if not _api_allowed(_client_ip(), 300):
            return jsonify({"error": "rate_limited"}), 429
    return None


# --- UI ROUTES ---
@app.route('/statistics')
def statistics_portal():
    return render_template('statistics.html')


@app.route('/')
def main_allotment():
    return render_template('index.html')


@app.route('/predictor')
def rank_predictor():
    return render_template('predictor.html')


@app.route('/resizer')
def photo_resizer():
    return render_template('resizer.html')


@app.route('/trends')
def trends_portal():
    # trends.html no longer exists — point visitors at the statistics dashboard.
    return redirect(url_for('statistics_portal'))


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(BASE_DIR, 'sitemap.xml')


# --- API ROUTES ---

# --- STATISTICS DASHBOARD API ROUTES ---

@app.route('/api/stats/kpi')
def get_stats_kpi():
    """KPI cards: total colleges, total courses, lowest cutoff rank, last cutoff rank, most competitive branch."""
    year = request.args.get('year', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q_where = f"WHERE rank > 0 {STATS_PHASE_SQL}"
        params = []
        if year:
            q_where += " AND year = ?"
            params.append(int(year))

        cursor.execute(f"SELECT COUNT(DISTINCT college_name) FROM colleges {q_where}", params)
        total_colleges = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(DISTINCT course_name) FROM colleges {q_where}", params)
        total_courses = cursor.fetchone()[0]

        cursor.execute(f"SELECT MIN(rank) FROM colleges {q_where} AND seat_type = 'SM'", params)
        lowest_cutoff = cursor.fetchone()[0] or 0

        cursor.execute(f"SELECT MAX(rank) FROM colleges {q_where} AND seat_type = 'SM'", params)
        last_cutoff = cursor.fetchone()[0] or 0

        # Most competitive = branch with the lowest non-zero cutoff in SM seat type
        cursor.execute(f"SELECT course_name, MIN(rank) as cutoff FROM colleges {q_where} AND seat_type = 'SM' GROUP BY course_name ORDER BY cutoff ASC LIMIT 1", params)
        top_row = cursor.fetchone()
        top_branch = top_row['course_name'] if top_row else '—'

        return jsonify({
            "total_colleges": total_colleges,
            "total_courses": total_courses,
            "lowest_cutoff": lowest_cutoff,
            "last_cutoff": last_cutoff,
            "top_branch": top_branch
        })
    except Exception:
        return jsonify({"total_colleges": 0, "total_courses": 0, "lowest_cutoff": 0, "last_cutoff": 0, "top_branch": "—"})
    finally:
        if conn: conn.close()


@app.route('/api/stats/top-colleges')
def get_stats_top_colleges():
    """Top 10 most competitive colleges for a given course (lowest + last SM cutoff)."""
    year = request.args.get('year', '').strip()
    course = request.args.get('course', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q = f"SELECT college_name, MIN(rank) as lowest, MAX(rank) as last FROM colleges WHERE rank > 0 AND seat_type = 'SM' {STATS_PHASE_SQL}"
        params = []
        if year:
            q += " AND year = ?"
            params.append(int(year))
        if course:
            q += " AND course_name LIKE ?"
            params.append(f"{course}%")
        q += " GROUP BY college_name ORDER BY lowest ASC LIMIT 10"
        cursor.execute(q, params)
        return jsonify([{"college": row['college_name'], "cutoff": row['lowest'], "last": row['last']} for row in cursor.fetchall()])
    except Exception:
        return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/stats/rank-bands')
def get_stats_rank_bands():
    """Seat count per category (replaces meaningless rank-band chart)."""
    year = request.args.get('year', '').strip()
    college = request.args.get('college', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q = f"SELECT seat_type, COUNT(*) as seats FROM colleges WHERE rank > 0 {STATS_PHASE_SQL}"
        params = []
        if year:
            q += " AND year = ?"
            params.append(int(year))
        if college:
            q += " AND college_name = ?"
            params.append(college)
        q += " GROUP BY seat_type ORDER BY seats DESC"
        cursor.execute(q, params)
        return jsonify([{"band": row['seat_type'], "seats": row['seats']} for row in cursor.fetchall()])
    except Exception:
        return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/stats/phase-trends')
def get_stats_phase_trends():
    """Phase-wise cutoff comparison for top branches (SM category). Only real phases."""
    year = request.args.get('year', '').strip()
    college = request.args.get('college', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        q_where = f"WHERE rank > 0 AND seat_type = 'SM' {STATS_PHASE_SQL}"
        params = []
        if year:
            q_where += " AND year = ?"
            params.append(int(year))
        if college:
            q_where += " AND college_name = ?"
            params.append(college)

        # Get top 8 courses by lowest cutoff
        cursor.execute(f"SELECT course_name, MIN(rank) as cutoff FROM colleges {q_where} GROUP BY course_name ORDER BY cutoff ASC LIMIT 8", params)
        top_courses = [row['course_name'] for row in cursor.fetchall()]
        if not top_courses:
            return jsonify({"phases": [], "courses": [], "data": {}})

        # Get only real phases present
        cursor.execute(f"SELECT DISTINCT phase FROM colleges {q_where}", params)
        phases = sorted([row['phase'] for row in cursor.fetchall()])

        # Build data: phase -> course -> cutoff
        data = {}
        for phase in phases:
            data[phase] = {}
            placeholders = ','.join(['?'] * len(top_courses))
            q = f"SELECT course_name, MIN(rank) as cutoff FROM colleges {q_where} AND phase = ? AND course_name IN ({placeholders}) GROUP BY course_name"
            p = list(params) + [phase] + top_courses
            cursor.execute(q, p)
            for row in cursor.fetchall():
                data[phase][row['course_name']] = row['cutoff']

        return jsonify({"phases": phases, "courses": top_courses, "data": data})
    except Exception:
        return jsonify({"phases": [], "courses": [], "data": {}})
    finally:
        if conn: conn.close()


@app.route('/api/stats/category-spread')
def get_stats_category_spread():
    """Category-wise closing rank spread: best (lowest cutoff), avg, worst (last cutoff)."""
    year = request.args.get('year', '').strip()
    college = request.args.get('college', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q = f"SELECT candidate_category, MIN(rank) as best, CAST(AVG(rank) AS INTEGER) as avg, MAX(rank) as worst FROM colleges WHERE rank > 0 {STATS_PHASE_SQL}"
        params = []
        if year:
            q += " AND year = ?"
            params.append(int(year))
        if college:
            q += " AND college_name = ?"
            params.append(college)
        q += " GROUP BY candidate_category ORDER BY best ASC"
        cursor.execute(q, params)

        result = {}
        for row in cursor.fetchall():
            cat = row['candidate_category'].strip()
            result[cat] = {"best": row['best'], "avg": row['avg'], "worst": row['worst']}
        return jsonify(result)
    except Exception:
        return jsonify({})
    finally:
        if conn: conn.close()


@app.route('/api/stats/college-cutoffs')
def get_stats_college_cutoffs():
    """Branch-wise lowest + last cutoff for a specific college."""
    year = request.args.get('year', '').strip()
    college = request.args.get('college', '').strip()
    if not college:
        return jsonify([]), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q = f"SELECT course_name, MIN(rank) as lowest, MAX(rank) as last, COUNT(*) as seats FROM colleges WHERE rank > 0 AND seat_type = 'SM' AND college_name = ? {STATS_PHASE_SQL}"
        params = [college]
        if year:
            q += " AND year = ?"
            params.append(int(year))
        q += " GROUP BY course_name ORDER BY lowest ASC"
        cursor.execute(q, params)
        return jsonify([{"course": row['course_name'], "lowest": row['lowest'], "last": row['last'], "seats": row['seats']} for row in cursor.fetchall()])
    except Exception:
        return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/stats/top-branches')
def get_stats_top_branches():
    """Most competitive branches by lowest SM cutoff + last cutoff."""
    year = request.args.get('year', '').strip()
    college = request.args.get('college', '').strip()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q = f"SELECT course_name, MIN(rank) as cutoff, MAX(rank) as last FROM colleges WHERE rank > 0 AND seat_type = 'SM' {STATS_PHASE_SQL}"
        params = []
        if year:
            q += " AND year = ?"
            params.append(int(year))
        if college:
            q += " AND college_name = ?"
            params.append(college)
        q += " GROUP BY course_name ORDER BY cutoff ASC LIMIT 15"
        cursor.execute(q, params)
        return jsonify([{"course": row['course_name'], "cutoff": row['cutoff'], "last": row['last']} for row in cursor.fetchall()])
    except Exception:
        return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/stats/cutoff-matrix')
def get_stats_cutoff_matrix():
    """SM lowest/last cutoff + seat count per college × course.
    Powers the College×Course heatmap and the opening-vs-closing scatter."""
    year = request.args.get('year', '').strip()
    phase = request.args.get('phase', '').strip() or 'Phase3'
    seat = request.args.get('seat', '').strip() or 'SM'
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        q = ("SELECT college_name, course_name, MIN(rank) AS lowest, MAX(rank) AS last, COUNT(*) AS seats "
             "FROM colleges WHERE rank > 0 AND phase = ? AND seat_type = ?")
        params = [phase, seat]
        if year:
            q += " AND year = ?"
            params.append(int(year))
        q += " GROUP BY college_name, course_name"
        cursor.execute(q, params)
        return jsonify([{"college": row['college_name'], "course": row['course_name'],
                         "lowest": row['lowest'], "last": row['last'], "seats": row['seats']}
                        for row in cursor.fetchall()])
    except Exception:
        return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/stats')
def get_database_stats():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM colleges")
        total_rows = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT college_name) FROM colleges")
        unique_colleges = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT year) FROM colleges")
        total_years = cursor.fetchone()[0]
        return jsonify({"total_rows": total_rows, "unique_colleges": unique_colleges, "total_years": total_years})
    except Exception:
        return jsonify({"total_rows": 0, "unique_colleges": 0, "total_years": 0})
    finally:
        if conn: conn.close()


@app.route('/api/advanced-stats')
def get_advanced_stats():
    college = request.args.get('college', '').strip()
    if not college:
        return jsonify({"error": "Missing college parameter"}), 400

    # Read multi-select array inputs from parameters
    selected_courses = request.args.getlist('courses[]')
    selected_years = request.args.getlist('years[]')
    selected_phases = request.args.getlist('phases[]')
    selected_categories = request.args.getlist('categories[]')
    selected_seats = request.args.getlist('seats[]')
    max_rank = request.args.get('max_rank', '').strip()

    # Enforce safe analytics default assignments on the backend
    if not selected_years or selected_years == ['']:
        selected_years = ['2026']
    if not selected_phases or selected_phases == ['']:
        selected_phases = ['Phase1']
    if not selected_categories or selected_categories == ['']:
        selected_categories = ['GN', 'SM']
    if not selected_seats or selected_seats == ['']:
        selected_seats = ['SM']

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT year, phase, candidate_category, course_name, seat_type,
                   MIN(rank) as cutoff_rank, COUNT(appl_no) as total_seats
            FROM colleges
            WHERE college_name = ? AND rank > 0
        """
        params = [college]

        if selected_courses and selected_courses[0] != '':
            query += " AND course_name IN ({})".format(','.join(['?'] * len(selected_courses)))
            params.extend(selected_courses)

        if selected_years:
            query += " AND year IN ({})".format(','.join(['?'] * len(selected_years)))
            params.extend([int(y) for y in selected_years])

        if selected_phases:
            query += " AND phase IN ({})".format(','.join(['?'] * len(selected_phases)))
            params.extend(selected_phases)

        if selected_categories:
            query += " AND candidate_category IN ({})".format(','.join(['?'] * len(selected_categories)))
            params.extend(selected_categories)

        if selected_seats:
            query += " AND seat_type IN ({})".format(','.join(['?'] * len(selected_seats)))
            params.extend(selected_seats)

        if max_rank and max_rank.isdigit():
            query += " AND rank <= ?"
            params.append(int(max_rank))

        query += " GROUP BY year, phase, candidate_category, course_name, seat_type ORDER BY course_name ASC, year ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        years_found = sorted(list(set(row['year'] for row in rows)))
        courses_found = sorted(list(set(row['course_name'] for row in rows)))

        chart_series = {}
        table_matrix = []

        for row in rows:
            yr = row['year']
            crs = row['course_name']
            cat = row['candidate_category']
            cutoff = row['cutoff_rank']
            seats = row['total_seats']

            table_matrix.append({
                "year": yr, "phase": row['phase'], "category": cat,
                "course": crs, "seat_type": row['seat_type'],
                "cutoff": cutoff, "seats": seats
            })

            series_key = f"{yr} - {cat}"
            if series_key not in chart_series:
                chart_series[series_key] = {}
            chart_series[series_key][crs] = cutoff

        return jsonify({
            "years": years_found,
            "courses": courses_found,
            "chart_series": chart_series,
            "table_matrix": table_matrix
        })
    except Exception:
        return jsonify({"error": "internal_error"}), 500
    finally:
        if conn: conn.close()


@app.route('/api/years')
def get_available_years():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT year FROM colleges WHERE year IS NOT NULL ORDER BY year DESC")
        return jsonify([row['year'] for row in cursor.fetchall()])
    except Exception: return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/categories')
def get_categories():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT candidate_category FROM colleges WHERE candidate_category IS NOT NULL AND candidate_category != '' ORDER BY candidate_category ASC")
        # Stripping whitespace so the dropdown is clean
        return jsonify(sorted(list(set([row['candidate_category'].strip() for row in cursor.fetchall()]))))
    except Exception: return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/colleges')
def get_colleges():
    conn = None
    try:
        course_filter = request.args.get('course', '').strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT DISTINCT college_name FROM colleges WHERE college_name IS NOT NULL AND college_name != ''"
        params = []
        if course_filter:
            query += " AND course_name = ?"
            params.append(course_filter)
        query += " ORDER BY college_name ASC"
        cursor.execute(query, params)
        return jsonify(sorted(list(set([row['college_name'].strip() for row in cursor.fetchall()]))))
    except Exception: return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/courses')
def get_courses():
    conn = None
    try:
        college_filter = request.args.get('college', '').strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT DISTINCT course_name FROM colleges WHERE course_name IS NOT NULL AND course_name != ''"
        params = []
        if college_filter:
            query += " AND college_name = ?"
            params.append(college_filter)
        query += " ORDER BY course_name ASC"
        cursor.execute(query, params)
        return jsonify(sorted(list(set([row['course_name'].strip() for row in cursor.fetchall()]))))
    except Exception: return jsonify([])
    finally:
        if conn: conn.close()


@app.route('/api/rank-summary')
def get_rank_summary():
    college = request.args.get('college', '').strip()
    course = request.args.get('course', '').strip()
    year = request.args.get('year', '').strip()
    if not college or not course: return jsonify([])
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT candidate_category, MIN(rank) as start_rank, MAX(rank) as end_rank FROM colleges WHERE college_name = ? AND course_name = ?"
        params = [college, course]
        if year:
            query += " AND year = ?"
            params.append(int(year))
        query += " GROUP BY candidate_category ORDER BY start_rank ASC"
        cursor.execute(query, params)
        return jsonify([{"category": row['candidate_category'], "start": row['start_rank'], "end": row['end_rank']} for row in cursor.fetchall()])
    except Exception:
        return jsonify({"error": "internal_error"}), 500
    finally:
        if conn: conn.close()


@app.route('/api/trends')
def get_cutoff_trends():
    college = request.args.get('college', '').strip()
    course = request.args.get('course', '').strip()

    if not college or not course:
        return jsonify({"error": "Missing college or course parameter"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT year, candidate_category, MIN(rank) as cutoff_rank
            FROM colleges
            WHERE college_name = ?
              AND course_name = ?
              AND rank > 0
            GROUP BY year, candidate_category
            ORDER BY year ASC, cutoff_rank ASC
        """
        cursor.execute(query, [college, course])
        rows = cursor.fetchall()

        trend_data = {}
        for row in rows:
            year = row['year']
            cat = row['candidate_category']
            cutoff = row['cutoff_rank']

            if cat not in trend_data:
                trend_data[cat] = {}
            trend_data[cat][year] = cutoff

        return jsonify(trend_data)
    except Exception:
        return jsonify({"error": "internal_error"}), 500
    finally:
        if conn:
            conn.close()


@app.route('/data')
def data():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            draw = max(int(request.args.get('draw', 1)), 1)
            start = min(max(int(request.args.get('start', 0)), 0), 10000000)
            length = min(max(int(request.args.get('length', 25)), 1), 1000)
        except (TypeError, ValueError):
            draw, start, length = 1, 0, 25

        year = request.args.get('year', '').strip()
        phase_raw = request.args.get('phase', '').strip()
        college = request.args.get('college', '').strip()
        course = request.args.get('course', '').strip()
        category_raw = request.args.get('category', '').strip()
        seat = request.args.get('seat', '').strip()
        search_rank = request.args.get('rank', '').strip()
        search_reg = request.args.get('reg_no', '').strip()

        query = "SELECT * FROM colleges WHERE 1=1"
        params = []

        if year:
            query += " AND year = ?"
            params.append(int(year))

        # ==========================================
        # MULTI-CHOICE PHASE FILTER
        # ==========================================
        if phase_raw:
            phases = [p.strip() for p in phase_raw.split(',') if p.strip()]
            if phases:
                phase_conditions = []
                for p in phases:
                    if p == "ProvisionalPhase1":
                        phase_conditions.append("(phase = 'ProvisionalPhase1' OR UPPER(phase) LIKE '%PROVISIONAL%')")
                    elif p == "Phase1":
                        phase_conditions.append("(phase = 'Phase1' OR phase = 'Phase 1')")
                    else:
                        phase_conditions.append("phase = ?")
                        params.append(p)

                if phase_conditions:
                    query += " AND (" + " OR ".join(phase_conditions) + ")"
        else:
            # No phase selected → real allotment phases only (no trial/provisional)
            query += " AND phase IN ('Phase1','Phase2','Phase3')"

        # ==========================================
        # MULTI-CHOICE CATEGORY FILTER
        # Using LIKE to match substrings and ignore case/trailing spaces
        # ==========================================
        if category_raw:
            categories = [c.strip() for c in category_raw.split(',') if c.strip()]
            if categories:
                cat_conditions = ["UPPER(candidate_category) LIKE UPPER(?)"] * len(categories)
                query += " AND (" + " OR ".join(cat_conditions) + ")"
                params.extend([f"%{c}%" for c in categories])

        if college:
            query += " AND college_name = ?"
            params.append(college)
        if course:
            query += " AND course_name = ?"
            params.append(course)
        if seat:
            query += " AND UPPER(seat_type) LIKE UPPER(?)"
            params.append(f"%{seat}%")

        if search_rank:
            query += " AND rank = ?"
            params.append(int(search_rank) if search_rank.isdigit() else 0)

        if search_reg:
            query += " AND (register_number = ? OR appl_no = ?)"
            params.extend([search_reg, search_reg])

        if not phase_raw:
            cursor.execute("SELECT COUNT(*) FROM colleges WHERE phase IN ('Phase1','Phase2','Phase3')")
        else:
            cursor.execute("SELECT COUNT(*) FROM colleges")
        total_records = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM ({query})", params)
        total_filtered = cursor.fetchone()[0]

        query += " ORDER BY rank ASC LIMIT ? OFFSET ?"
        params.extend([length, start])
        cursor.execute(query, params)

        data_list = []
        for row in cursor.fetchall():
            reg_val = row['register_number'] if row['register_number'] else (row['appl_no'] if row['appl_no'] else 'N/A')
            rank_val = row['rank'] if row['rank'] and int(row['rank']) > 0 else 'N/A'

            data_list.append({
                'year': row['year'],
                'phase': row['phase'],
                'register_number': reg_val,
                'rank': rank_val,
                'college_name': row['college_name'],
                'course_name': row['course_name'],
                'candidate_category': row['candidate_category'],
                'seat_type': row['seat_type']
            })

        return jsonify({"draw": draw, "recordsTotal": total_records, "recordsFiltered": total_filtered, "data": data_list})
    except Exception:
        return jsonify({"draw": 1, "recordsTotal": 0, "recordsFiltered": 0, "data": []}), 500
    finally:
        if conn: conn.close()


@app.route('/api/migrations')
def get_migrations():
    year = request.args.get('year', '').strip()
    from_phase = request.args.get('from_phase', '').strip()
    to_phase = request.args.get('to_phase', '').strip()
    college = request.args.get('college', '').strip()
    course = request.args.get('course', '').strip()

    if not year or not from_phase or not to_phase:
        return jsonify({"error": "Missing required parameters: year, from_phase, to_phase"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Find students who were in from_phase and also appear in to_phase (same year)
        # but with a DIFFERENT college_name — i.e., they "jumped" colleges.
        # appl_no and register_number are always the same, so just join on appl_no.
        query = """
            SELECT
                a.appl_no,
                a.rank,
                a.college_name   AS from_college,
                a.course_name    AS from_course,
                b.college_name   AS to_college,
                b.course_name    AS to_course,
                a.candidate_category,
                a.seat_type
            FROM colleges a
            INNER JOIN colleges b
                ON  a.year = b.year
                AND a.appl_no = b.appl_no
                AND a.appl_no IS NOT NULL
                AND a.appl_no != ''
            WHERE a.year = ?
              AND a.phase = ?
              AND b.phase = ?
              AND (a.college_name != b.college_name OR a.course_name != b.course_name)
        """
        params = [int(year), from_phase, to_phase]

        if college:
            query += " AND (a.college_name = ? OR b.college_name = ?)"
            params.extend([college, college])
        if course:
            query += " AND (a.course_name = ? OR b.course_name = ?)"
            params.extend([course, course])

        query += " ORDER BY a.rank ASC LIMIT 500"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        migrations = []
        for row in rows:
            migrations.append({
                "appl_no": row["appl_no"] or "N/A",
                "rank": row["rank"] if row["rank"] and int(row["rank"]) > 0 else "N/A",
                "from_college": row["from_college"],
                "from_course": row["from_course"],
                "to_college": row["to_college"],
                "to_course": row["to_course"],
                "category": row["candidate_category"],
                "seat_type": row["seat_type"]
            })

        # Summary stats: count how many jumped TO each college and FROM each college
        jumped_to = {}
        jumped_from = {}
        for m in migrations:
            jumped_to[m["to_college"]] = jumped_to.get(m["to_college"], 0) + 1
            jumped_from[m["from_college"]] = jumped_from.get(m["from_college"], 0) + 1

        top_destinations = sorted(jumped_to.items(), key=lambda x: x[1], reverse=True)[:10]
        top_sources = sorted(jumped_from.items(), key=lambda x: x[1], reverse=True)[:10]

        return jsonify({
            "total_migrations": len(migrations),
            "migrations": migrations,
            "top_destinations": [{"college": c, "count": n} for c, n in top_destinations],
            "top_sources": [{"college": c, "count": n} for c, n in top_sources]
        })
    except Exception:
        return jsonify({"error": "internal_error"}), 500
    finally:
        if conn: conn.close()


@app.after_request
def add_security_headers(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    resp.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    resp.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
    # Never cache HTML pages: stale copies keep old CSP headers that can
    # block CDN scripts (caused blank tables after the CSP was tightened).
    if resp.content_type.startswith('text/html'):
        resp.headers.setdefault('Cache-Control', 'no-cache, no-store, must-revalidate')
        resp.headers.setdefault('Pragma', 'no-cache')
    resp.headers.setdefault(
        'Content-Security-Policy',
        "default-src 'self'; script-src 'self' 'unsafe-inline' https://code.jquery.com "
        "https://cdn.jsdelivr.net https://cdn.datatables.net "
        "https://cdnjs.cloudflare.com https://static.cloudflareinsights.com; style-src 'self' "
        "'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.datatables.net "
        "https://cdnjs.cloudflare.com; img-src 'self' data: blob: https:; "
        "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; connect-src 'self' blob: "
        "https://static.cloudflareinsights.com https://cloudflareinsights.com; frame-ancestors 'none'; base-uri 'self'; object-src 'none'; "
        "worker-src 'self' blob: https://cdnjs.cloudflare.com"
    )
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=os.environ.get('FLASK_DEBUG') == '1')
