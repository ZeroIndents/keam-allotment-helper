"""
KEAM Allotment / Cutoff PDF -> SQLite parser
=============================================

Reads CEE Kerala (KEAM) allotment and cutoff PDFs from PDF_FOLDER and loads
them into a SQLite database for use on your site.

Requirements (install once):
    pip install pypdf pdfplumber pdf2image pytesseract tqdm --break-system-packages
    (system) poppler-utils (for pdf2image) + tesseract-ocr (for OCR fallback)

--------------------------------------------------------------------------
HOW FORMAT-FLEXIBILITY WORKS
--------------------------------------------------------------------------
CEE changes the PDF layout every year (sometimes every phase). Instead of
hard-coding column positions, this script:

  1. Detects which *kind* of document a PDF is (allotment list, cutoff
     matrix, or scanned image) by sniffing header keywords on page 1.
  2. For table-shaped PDFs (like the current 2026 allotment list), it reads
     the PDF's own ruling lines via pdfplumber and rebuilds the header from
     row(s) at the top of the table -- so it doesn't care which column order
     CEE used, only what the header *says* each column is (via
     HEADER_SYNONYMS below). Add new header spellings there, not in the
     parsing logic.
  3. If a PDF has no ruling lines (pure flowing text), it falls back to a
     regex line-grouping parser that looks for a row-start pattern
     (SlNo, ApplNo, Rank, Category ...) and re-assembles wrapped lines.
  4. If a PDF has no digital text layer at all, it OCRs the pages.

To support a genuinely new layout in future (e.g. a KCET-style matrix, or a
different exam board entirely), add one new `detect_*` / `parse_*` function
pair and register it in FORMAT_HANDLERS -- everything else (dictionaries,
DB schema, dedup logic) stays the same.
--------------------------------------------------------------------------
"""

import sqlite3
import os
import re
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # table-based parsing will be skipped with a warning

# The Sandbox Database Configuration
DB_PATH = '/var/lib/college_project/colleges_v2.db'
PDF_FOLDER = 'pdf_source'

# ==========================================================================
# Master Alias Dictionaries -- DO NOT MODIFY. Everything else in the script
# is built to work around these, not the other way around.
# ==========================================================================
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
    "EKC": "Eranad Knowledge City Technical Campus, Malappuram", "FIT": "Federal Institute of Science and Technology (FISAT), Ernakulam",
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

# Auto-format target names to embed Short Codes
KEAM_COLLEGES_FORMATTED = {code: f"{code} - {name}" for code, name in KEAM_COLLEGES.items()}
KEAM_COURSES_FORMATTED = {code: f"{code} - {name}" for code, name in KEAM_COURSES.items()}

# Expected category mapping ordering for Cutoff Matrix lists (unchanged --
# only used by the cutoff-matrix parsers below)
MATRIX_CATEGORIES = ['SM', 'EZ', 'MU', 'LA', 'BH', 'DV', 'VK', 'BX', 'KN', 'KU', 'SC', 'ST', 'EW']

# ==========================================================================
# Header vocabulary for the row-per-candidate "allotment list" format.
# Add new spellings here (e.g. if a future PDF says "Application Number"
# instead of "ApplNo") -- you should NOT need to touch the parsing logic.
# Keys are the header text with all whitespace/punctuation stripped and
# upper-cased, values are the internal field name we standardize on.
# ==========================================================================
HEADER_SYNONYMS = {
    'SLNO': 'sl_no', 'SLNUMBER': 'sl_no', 'SNO': 'sl_no',
    'APPLNO': 'appl_no', 'APPLICATIONNO': 'appl_no', 'APPLICATIONNUMBER': 'appl_no', 'APPNO': 'appl_no',
    'RANK': 'rank', 'ALLOTMENTRANK': 'rank',
    'CANDIDATECATEGORY': 'category', 'CATEGORY': 'category', 'COMMUNITY': 'category', 'ALLOTTEDCATEGORY': 'category',
    'COLLEGENAME': 'college', 'COLLEGE': 'college', 'INSTITUTION': 'college',
    'COURSENAME': 'course', 'COURSE': 'course', 'BRANCH': 'course', 'PROGRAMME': 'course', 'PROGRAM': 'course',
    'SEATTYPE': 'seat_type', 'SEAT': 'seat_type', 'ALLOTMENTTYPE': 'seat_type', 'QUOTA': 'seat_type',
}
# A row is only usable if it has at least these fields
REQUIRED_ALLOTMENT_FIELDS = {'appl_no', 'rank', 'college', 'course'}


# ==========================================================================
# Database
# ==========================================================================
def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colleges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER, phase TEXT, appl_no TEXT, register_number TEXT, rank INTEGER,
            candidate_category TEXT, college_name TEXT, course_name TEXT, seat_type TEXT
        )
    ''')

    # Migration: add sl_no if this DB pre-dates the allotment-list format.
    # (Kept nullable/optional so it never breaks old cutoff-matrix rows.)
    cursor.execute("PRAGMA table_info(colleges)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if 'sl_no' not in existing_cols:
        cursor.execute("ALTER TABLE colleges ADD COLUMN sl_no TEXT")

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fast_matrix ON colleges(year, phase, candidate_category, college_name, course_name, rank)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fast_line ON colleges(year, phase, appl_no, college_name, course_name)')

    conn.commit()
    return conn


def insert_record(cursor, year, phase, appl_no, rank, category, college, course, seat_type, sl_no=None):
    reg_no = appl_no

    if appl_no == "CUTOFF":
        cursor.execute('''SELECT 1 FROM colleges WHERE year=? AND phase=? AND candidate_category=? AND college_name=? AND course_name=? AND rank=?''',
                       (year, phase, category, college, course, rank))
    else:
        cursor.execute('''SELECT 1 FROM colleges WHERE year=? AND phase=? AND appl_no=? AND college_name=? AND course_name=?''',
                       (year, phase, appl_no, college, course))

    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO colleges (year, phase, appl_no, register_number, rank, candidate_category, college_name, course_name, seat_type, sl_no)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (year, phase, appl_no, reg_no, rank, category, college, course, seat_type, sl_no))
        return 1
    return 0


# ==========================================================================
# Shared helpers -- resolving "CODE- Name" text against the dictionaries
# ==========================================================================
def _clean_cell(text):
    if text is None:
        return ''
    return re.sub(r'\s+', ' ', str(text).replace('\n', ' ')).strip()


def resolve_college(raw_text):
    """
    'TVE- College of Engineering, Thiruvananthapuram' (possibly wrapped
    across lines) -> ('TVE - College of Engineering, Thiruvananthapuram', 'TVE')

    Falls back to the cleaned raw text (unmapped) if the code isn't in
    KEAM_COLLEGES, so nothing is silently dropped -- it's just flagged.
    """
    cleaned = _clean_cell(raw_text)
    match = re.match(r'^([A-Za-z]{2,4})\s*[-.]\s*', cleaned)
    if match:
        code = match.group(1).upper()
        if code in KEAM_COLLEGES_FORMATTED:
            return KEAM_COLLEGES_FORMATTED[code], code
    # Fallback: scan for any known code as a whole word anywhere in the cell
    for code in KEAM_COLLEGES:
        if re.search(rf'\b{code}\b', cleaned.upper()):
            return KEAM_COLLEGES_FORMATTED[code], code
    return cleaned, None


def resolve_course(raw_text):
    """Same idea as resolve_college, against KEAM_COURSES."""
    cleaned = _clean_cell(raw_text)
    match = re.match(r'^([A-Za-z]{2})\s*[-.]\s*', cleaned)
    if match:
        code = match.group(1).upper()
        if code in KEAM_COURSES_FORMATTED:
            return KEAM_COURSES_FORMATTED[code], code
    for code in KEAM_COURSES:
        if re.search(rf'\b{code}\b', cleaned.upper()):
            return KEAM_COURSES_FORMATTED[code], code
    return cleaned, None


def extract_seat_type(tail):
    """
    Pull the Seat Type code out of a fallback-parsed row tail.

    In Phase3-style PDFs a Remarks column follows the Seat Type column and
    its text lands in the same tail buffer (e.g. '...Engineering SM No
    change of Allotment'). Every known remark mentions 'Allotment', so cut
    the tail at the earliest remark marker before matching the trailing
    2-letter code. When there is no remarks column, nothing is cut and the
    end-anchored match behaves exactly as before.
    """
    lower = tail.lower()
    cut_idx = len(tail)
    for marker in ('no change of allotment', 'change of allotment', 'fresh allotment', 'allotment'):
        pos = lower.find(marker)
        if pos != -1 and pos < cut_idx:
            cut_idx = pos
    if cut_idx < len(tail):
        tail = tail[:cut_idx]
    match = re.search(r'\b([A-Z]{2}(?:-[A-Z]{2})?)\s*#?\s*$', tail)
    return match.group(1) if match else ''


# ==========================================================================
# FORMAT 1: Allotment list (row-per-candidate) -- e.g. 2026_Provisional_Phase1.pdf
#   SlNo | ApplNo | Rank | Candidate Category | College Name | Course Name | Seat Type
# ==========================================================================
def looks_like_allotment_list(compressed_upper_text):
    return 'SLNO' in compressed_upper_text and 'APPLNO' in compressed_upper_text and 'RANK' in compressed_upper_text


def build_header_column_map(table, max_header_rows=4):
    """
    Merges the (possibly multi-row) header of a pdfplumber table into one
    label per column, matches each against HEADER_SYNONYMS, and returns
    (field_name -> column_index, index_of_first_data_row).
    Returns None if the required fields aren't all found.
    """
    if not table:
        return None
    ncols = len(table[0])
    merged = [''] * ncols
    data_start = 0

    for i in range(min(max_header_rows, len(table))):
        row = table[i]
        first_cell = _clean_cell(row[0]) if row else ''
        if first_cell.isdigit():
            data_start = i
            break
        for c in range(min(ncols, len(row))):
            if row[c]:
                merged[c] += ' ' + str(row[c])
        data_start = i + 1

    normalized = [re.sub(r'[^A-Z]', '', m.upper()) for m in merged]
    field_idx = {}
    for idx, norm in enumerate(normalized):
        if norm in HEADER_SYNONYMS:
            field_idx.setdefault(HEADER_SYNONYMS[norm], idx)

    if not REQUIRED_ALLOTMENT_FIELDS.issubset(field_idx.keys()):
        return None
    return field_idx, data_start


def parse_allotment_list_pdf(filepath, year, phase, cursor):
    """
    Primary parser for the current table-based allotment list format.
    Uses the PDF's own ruling lines (via pdfplumber) to read each row, so
    it's immune to column-width/wrapping quirks that break naive text
    regexing.

    Returns (rows_inserted, pages_with_usable_table). The second value is
    what callers should check before falling back to another parser --
    rows_inserted can legitimately be 0 on a re-import (dedup working as
    intended), which is different from "this PDF has no table structure".
    """
    if pdfplumber is None:
        print("    [X] pdfplumber not installed -- run: pip install pdfplumber --break-system-packages")
        print("        Falling back to the text regex parser; prefer pdfplumber for the table-based format.")
        return 0, 0

    row_count = 0
    pages_with_usable_table = 0  # distinct from row_count: dedup can legitimately yield 0 new rows
    unmapped_colleges, unmapped_courses = set(), set()

    with pdfplumber.open(filepath) as pdf:
        pbar = tqdm(pdf.pages, desc=f"Allotment list {os.path.basename(filepath)}", unit="page")
        for page in pbar:
            tables = page.extract_tables()
            if not tables:
                page.flush_cache()
                continue
            col_map = build_header_column_map(tables[0])
            if col_map is None:
                page.flush_cache()
                continue
            pages_with_usable_table += 1
            field_idx, data_start = col_map

            for row in tables[0][data_start:]:
                if not row or not row[0] or not _clean_cell(row[0]).isdigit():
                    continue  # blank spacer / stray row

                try:
                    sl_no = _clean_cell(row[field_idx['sl_no']]) if 'sl_no' in field_idx else None
                    appl_no = _clean_cell(row[field_idx['appl_no']])
                    rank_val = int(re.sub(r'\D', '', _clean_cell(row[field_idx['rank']])))
                    category = _clean_cell(row[field_idx['category']]) if 'category' in field_idx else ''
                    seat_type = _clean_cell(row[field_idx['seat_type']]) if 'seat_type' in field_idx else ''
                    college_raw = row[field_idx['college']]
                    course_raw = row[field_idx['course']]
                except (KeyError, ValueError, IndexError):
                    continue

                college_name, col_code = resolve_college(college_raw)
                course_name, crs_code = resolve_course(course_raw)
                if col_code is None:
                    unmapped_colleges.add(college_name)
                if crs_code is None:
                    unmapped_courses.add(course_name)

                added = insert_record(cursor, year, phase, appl_no, rank_val, category,
                                       college_name, course_name, seat_type, sl_no=sl_no)
                row_count += added
            page.flush_cache()
            pbar.set_postfix(rows=row_count)

    if unmapped_colleges:
        sample = sorted(unmapped_colleges)[:10]
        print(f"    [!] {len(unmapped_colleges)} college name(s) had no matching code in KEAM_COLLEGES "
              f"(stored as-is, add them to the dict to normalize): {sample}")
    if unmapped_courses:
        sample = sorted(unmapped_courses)[:10]
        print(f"    [!] {len(unmapped_courses)} course name(s) had no matching code in KEAM_COURSES "
              f"(stored as-is): {sample}")

    return row_count, pages_with_usable_table


def parse_allotment_list_text_fallback(filepath, year, phase, cursor, reader):
    """
    Fallback for allotment-list-shaped PDFs that have NO ruling lines
    (pure flowing text) -- e.g. if a future phase's PDF is exported
    differently. Groups wrapped lines by a "row start" regex instead of
    relying on table borders.
    """
    row_count = 0
    row_start_re = re.compile(r'^\s*(\d{1,6})\s+(\d{5,9})\s+(\d{1,6})\s+([A-Z]{2})\s+(.+)$')

    def flush(buf):
        nonlocal row_count
        if not buf:
            return
        tail = _clean_cell(buf['tail'])
        college_name, _ = resolve_college(tail)
        course_name, _ = resolve_course(tail)
        seat_type = extract_seat_type(tail)
        try:
            rank_val = int(buf['rank'])
        except ValueError:
            return
        row_count += insert_record(cursor, year, phase, buf['appl_no'], rank_val, buf['category'],
                                    college_name, course_name, seat_type, sl_no=buf['sl_no'])

    pbar = tqdm(reader.pages, desc=f"Allotment(text-fallback) {os.path.basename(filepath)}", unit="page")
    for page in pbar:
        text = page.extract_text() or ''
        buf = None
        for line in text.split('\n'):
            m = row_start_re.match(line)
            if m:
                flush(buf)
                buf = {'sl_no': m.group(1), 'appl_no': m.group(2), 'rank': m.group(3),
                       'category': m.group(4), 'tail': m.group(5)}
            elif buf:
                buf['tail'] += ' ' + line.strip()
        flush(buf)
        pbar.set_postfix(rows=row_count)

    return row_count


# ==========================================================================
# FORMAT 2: Cutoff matrix (rank cutoffs per category, per college/course)
#   -- this is the original layout the script was built for. Kept intact.
# ==========================================================================
def looks_like_cutoff_matrix(compressed_upper_text):
    return any(k in compressed_upper_text for k in ["LASTRANK", "THEFOLLOWINGTABLE", "SMEZMU"])


def parse_cutoff_matrix_digital(filepath, year, phase, cursor, reader):
    print(f"\n[+] Digital Matrix layout detected for {os.path.basename(filepath)}.")
    row_count = 0
    current_course = None

    pbar = tqdm(reader.pages, desc=f"Matrix parsing {os.path.basename(filepath)}", unit="page")
    for page in pbar:
        text = page.extract_text()
        if not text:
            continue
        lines = text.split('\n')
        for idx, line in enumerate(lines):
            line_str = line.strip()
            course_match = re.search(r'\b([A-Z]{2})\s*:\s*', line_str)
            if course_match and course_match.group(1) in KEAM_COURSES_FORMATTED:
                current_course = KEAM_COURSES_FORMATTED[course_match.group(1)]
                continue

            col_match = re.search(r'\b([A-Z]{3})\b', line_str)
            if col_match and current_course and col_match.group(1) in KEAM_COLLEGES_FORMATTED:
                col_code = col_match.group(1)
                clean_college = KEAM_COLLEGES_FORMATTED[col_code]

                data_pool = line_str
                look_ahead_idx = idx + 1
                while look_ahead_idx < len(lines):
                    next_line = lines[look_ahead_idx].strip()
                    if any(f" {c} " in f" {next_line} " for c in KEAM_COLLEGES) or ":" in next_line:
                        break
                    data_pool += " " + next_line
                    look_ahead_idx += 1

                rank_tokens = [r for r in re.findall(r'\b\d+\b', data_pool) if int(r) != year and int(r) < 100000]
                for c_idx, rank_str in enumerate(rank_tokens):
                    if c_idx < len(MATRIX_CATEGORIES):
                        added = insert_record(cursor, year, phase, "CUTOFF", int(rank_str),
                                               MATRIX_CATEGORIES[c_idx], clean_college, current_course, "SM")
                        row_count += added
        pbar.set_postfix(rows=row_count)

    return row_count


def parse_cutoff_matrix_ocr(filepath, year, phase, cursor):
    print(f"\n[!] {os.path.basename(filepath)}: No digital text found. Booting AI OCR (matrix mode)...")
    row_count = 0

    try:
        images = convert_from_path(filepath)
    except Exception as e:
        print(f"    [X] Could not rasterize {filepath}: {e}")
        return 0

    current_course = None
    pbar = tqdm(images, desc=f"OCR {os.path.basename(filepath)}", unit="page")
    for img in pbar:
        fixed_img = auto_rotate_for_ocr(img)
        text = pytesseract.image_to_string(fixed_img)
        lines = text.split('\n')

        for idx, line in enumerate(lines):
            line_str = line.strip().upper()
            if not line_str:
                continue

            course_match = re.search(r'\b([A-Z]{2})\s*[:\-]\s*[A-Z]', line_str)
            if course_match:
                crs_code = course_match.group(1)
                if crs_code in KEAM_COURSES_FORMATTED:
                    current_course = KEAM_COURSES_FORMATTED[crs_code]
                    continue

            col_code = None
            first_word = re.sub(r'[^A-Z]', '', line_str.split()[0]) if line_str.split() else ""

            if len(first_word) == 3 and first_word in KEAM_COLLEGES_FORMATTED:
                col_code = first_word
            elif "UCE" in line_str or "UNIVERSITY COLLEGE" in line_str:
                col_code = "UCE"
            elif "PRN" in line_str or "PERUMON" in line_str or "PAN |" in line_str:
                col_code = "PRN"
            elif "AJC" in line_str or "AMAL JYOTHI" in line_str or "AC [" in line_str:
                col_code = "AJC"
            elif "CEC" in line_str or "CHERTHALA" in line_str:
                col_code = "CEC"
            else:
                for code in KEAM_COLLEGES.keys():
                    if re.search(rf'\b{code}\b', line_str):
                        col_code = code
                        break

            if col_code and current_course:
                clean_college = KEAM_COLLEGES_FORMATTED[col_code]
                data_pool = line_str
                if idx + 1 < len(lines):
                    data_pool += " " + lines[idx + 1].strip()

                rank_tokens = re.findall(r'\b\d{4,5}\b', data_pool)
                for c_idx, rank_str in enumerate(rank_tokens):
                    if c_idx < len(MATRIX_CATEGORIES):
                        added = insert_record(cursor, year, phase, "CUTOFF", int(rank_str),
                                               MATRIX_CATEGORIES[c_idx], clean_college, current_course, "SM")
                        row_count += added

        pbar.set_postfix(rows=row_count)

    return row_count


def parse_allotment_list_ocr(filepath, year, phase, cursor):
    """OCR fallback for a scanned allotment-list-shaped PDF (row-per-candidate)."""
    print(f"\n[!] {os.path.basename(filepath)}: No digital text found. Booting AI OCR (allotment-list mode)...")
    row_count = 0
    row_start_re = re.compile(r'^\s*(\d{1,6})\s+(\d{5,9})\s+(\d{1,6})\s+([A-Z]{2})\s+(.+)$')

    try:
        images = convert_from_path(filepath)
    except Exception as e:
        print(f"    [X] Could not rasterize {filepath}: {e}")
        return 0

    def flush(buf):
        nonlocal row_count
        if not buf:
            return
        tail = _clean_cell(buf['tail'])
        college_name, _ = resolve_college(tail)
        course_name, _ = resolve_course(tail)
        seat_type = extract_seat_type(tail)
        try:
            rank_val = int(buf['rank'])
        except ValueError:
            return
        row_count += insert_record(cursor, year, phase, buf['appl_no'], rank_val, buf['category'],
                                    college_name, course_name, seat_type, sl_no=buf['sl_no'])

    pbar = tqdm(images, desc=f"OCR(allotment) {os.path.basename(filepath)}", unit="page")
    for img in pbar:
        fixed_img = auto_rotate_for_ocr(img)
        text = pytesseract.image_to_string(fixed_img)
        buf = None
        for line in text.upper().split('\n'):
            m = row_start_re.match(line)
            if m:
                flush(buf)
                buf = {'sl_no': m.group(1), 'appl_no': m.group(2), 'rank': m.group(3),
                       'category': m.group(4), 'tail': m.group(5)}
            elif buf:
                buf['tail'] += ' ' + line.strip()
        flush(buf)
        pbar.set_postfix(rows=row_count)

    return row_count


def auto_rotate_for_ocr(img):
    """
    Try to detect page orientation via Tesseract's OSD; fall back to the
    180-degree flip the original script hard-coded (some older CEE scans
    are uploaded upside-down). If OSD is unavailable/inconclusive, 180 is
    still the safest default for this document family.
    """
    try:
        osd = pytesseract.image_to_osd(img)
        angle_match = re.search(r'Rotate:\s*(\d+)', osd)
        if angle_match:
            angle = int(angle_match.group(1))
            if angle:
                return img.rotate(360 - angle, expand=True)
            return img
    except Exception:
        pass
    return img.rotate(180, expand=True)


# ==========================================================================
# Format detection + dispatch
# ==========================================================================
def get_sample_text(reader, num_pages=3):
    sample_text = ""
    for i in range(min(num_pages, len(reader.pages))):
        sample_text += (reader.pages[i].extract_text() or "")
    return sample_text


def detect_format(reader):
    """
    Returns one of: 'allotment_list', 'cutoff_matrix', 'scanned', 'unknown'

    To support a new PDF layout in future: write a `looks_like_X` detector
    following the pattern above, add it to this chain, and add matching
    parse_X_pdf / parse_X_ocr functions below.
    """
    sample_text = get_sample_text(reader)
    # Strip ALL non-alphanumerics, not just whitespace -- CEE writes the
    # header as "Sl.No" in some phases (dot survives a whitespace-only
    # squeeze and breaks the 'SLNO' check) and "SlNo" in others.
    compressed = re.sub(r'[^A-Z0-9]', '', sample_text.upper())

    if len(compressed) < 50:
        return 'scanned'
    if looks_like_allotment_list(compressed):
        return 'allotment_list'
    if looks_like_cutoff_matrix(compressed):
        return 'cutoff_matrix'
    return 'unknown'


def extract_year_phase_from_text(text):
    """
    Best-effort fallback for when the filename doesn't parse cleanly.
    Looks for 'KEAM 2026' style year mentions and common phase phrasing.
    """
    year = None
    year_match = re.search(r'\bKEAM\s*(\d{4})\b', text, re.IGNORECASE)
    if year_match:
        year = int(year_match.group(1))

    phase = None
    lowered = text.lower()
    if 'trial' in lowered:
        phase = 'Trial'
    elif 'first phase' in lowered and 'provisional' in lowered:
        phase = 'ProvisionalPhase1'
    elif 'first phase' in lowered:
        phase = 'Phase1'
    elif 'second phase' in lowered and 'provisional' in lowered:
        phase = 'ProvisionalPhase2'
    elif 'second phase' in lowered:
        phase = 'Phase2'
    elif 'third phase' in lowered and 'provisional' in lowered:
        phase = 'ProvisionalPhase3'
    elif 'third phase' in lowered:
        phase = 'Phase3'

    return year, phase


def parse_year_phase_from_filename(filename):
    """
    Smart phase normalizer -- fixes messy filenames to consistent
    dropdown-style values. Returns (year, phase) or (None, None) on failure.
    """
    try:
        year = int(filename.split('_')[0])
        raw_phase = filename.split('_')[1].split('.pdf')[0]
    except Exception:
        return None, None

    clean_phase = raw_phase.lower().replace(" ", "")
    if 'trial' in clean_phase:
        phase = 'Trial'
    elif 'provisional' in clean_phase and '3' in clean_phase:
        phase = 'ProvisionalPhase3'
    elif 'provisional' in clean_phase and '2' in clean_phase:
        phase = 'ProvisionalPhase2'
    elif 'provisional' in clean_phase and '1' in clean_phase:
        phase = 'ProvisionalPhase1'
    elif '1' in clean_phase:
        phase = 'Phase1'
    elif '2' in clean_phase:
        phase = 'Phase2'
    elif '3' in clean_phase:
        phase = 'Phase3'
    else:
        phase = raw_phase

    return year, phase


# ==========================================================================
# Main entry point
# ==========================================================================
def process_pdfs():
    conn = setup_database()
    cursor = conn.cursor()

    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"[*] Created missing directory: {PDF_FOLDER}. Place your PDFs there.")
        return

    for filename in os.listdir(PDF_FOLDER):
        if not filename.endswith('.pdf'):
            continue

        filepath = os.path.join(PDF_FOLDER, filename)
        reader = PdfReader(filepath)

        year, phase = parse_year_phase_from_filename(filename)
        if year is None or phase is None:
            content_year, content_phase = extract_year_phase_from_text(get_sample_text(reader))
            year = year or content_year or 2024
            phase = phase or content_phase or "Phase1"
            print(f"[!] {filename}: couldn't parse year/phase from filename, "
                  f"using year={year} phase={phase} (detected from PDF content where possible)")

        fmt = detect_format(reader)
        row_count = 0

        if fmt == 'allotment_list':
            row_count, pages_with_table = parse_allotment_list_pdf(filepath, year, phase, cursor)
            if pages_with_table == 0:
                # No ruling lines found anywhere (or pdfplumber missing) --
                # this is a genuine parse failure, not just dedup returning
                # 0 new rows on a re-import. Try the text-regrouping fallback.
                print(f"    [i] No table structure found in {filename}, trying text fallback...")
                row_count = parse_allotment_list_text_fallback(filepath, year, phase, cursor, reader)

        elif fmt == 'cutoff_matrix':
            row_count = parse_cutoff_matrix_digital(filepath, year, phase, cursor, reader)

        elif fmt == 'scanned':
            # Peek at OCR of page 1 to decide which scanned parser to use.
            try:
                first_page_img = convert_from_path(filepath, first_page=1, last_page=1)[0]
                probe_text = pytesseract.image_to_string(auto_rotate_for_ocr(first_page_img)).upper()
                probe_compressed = re.sub(r'[^A-Z0-9]', '', probe_text)
            except Exception:
                probe_compressed = ''

            if looks_like_allotment_list(probe_compressed):
                row_count = parse_allotment_list_ocr(filepath, year, phase, cursor)
            else:
                row_count = parse_cutoff_matrix_ocr(filepath, year, phase, cursor)

        else:
            print(f"[!] {filename}: unrecognized PDF layout -- skipping. "
                  f"Add a new looks_like_* detector + parser for this format.")
            continue

        conn.commit()
        print(f"[?] {filename}: {row_count} new row(s) inserted (year={year}, phase={phase}, format={fmt})")

    conn.close()


if __name__ == '__main__':
    process_pdfs()