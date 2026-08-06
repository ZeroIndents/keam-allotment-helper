import sqlite3
import os
import re
from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from tqdm import tqdm  # THE NEW PROGRESS BAR

# The Sandbox Database Configuration
DB_PATH = '/var/lib/college_project/colleges_v2.db'
PDF_FOLDER = 'pdf_source'

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

# Expected category mapping ordering for Cutoff Matrix lists
MATRIX_CATEGORIES = ['SM', 'EZ', 'MU', 'LA', 'BH', 'DV', 'VK', 'BX', 'KN', 'KU', 'SC', 'ST', 'EW']

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colleges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER, phase TEXT, appl_no TEXT, rank INTEGER,
            candidate_category TEXT, college_name TEXT, course_name TEXT, seat_type TEXT
        )
    ''')
    
    # --- THE MAGIC SPEED FIX ---
    # These indexes stop SQLite from freezing up by giving it a map to find duplicates instantly.
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fast_matrix ON colleges(year, phase, candidate_category, college_name, course_name, rank)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fast_line ON colleges(year, phase, appl_no, college_name, course_name)')
    
    conn.commit()
    return conn

def insert_record(cursor, year, phase, appl_no, rank, category, college, course, seat_type):
    # This lookup is now instantaneous thanks to the indexes above!
    if appl_no == "CUTOFF":
        cursor.execute('''SELECT 1 FROM colleges WHERE year=? AND phase=? AND candidate_category=? AND college_name=? AND course_name=? AND rank=?''', 
                       (year, phase, category, college, course, rank))
    else:
        cursor.execute('''SELECT 1 FROM colleges WHERE year=? AND phase=? AND appl_no=? AND college_name=? AND course_name=?''', 
                       (year, phase, appl_no, college, course))
                       
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO colleges (year, phase, appl_no, rank, candidate_category, college_name, course_name, seat_type) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (year, phase, appl_no, rank, category, college, course, seat_type))
        return 1
    return 0

def process_pdfs():
    conn = setup_database()
    cursor = conn.cursor()
    
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
        print(f"[*] Created missing directory: {PDF_FOLDER}. Place your PDFs there.")
        return

    for filename in os.listdir(PDF_FOLDER):
        if not filename.endswith('.pdf'): continue
        
        try:
            year = int(filename.split('_')[0])
            phase = filename.split('_')[1].split('.pdf')[0]
        except Exception:
            year = 2024
            phase = "Phase1"

        filepath = os.path.join(PDF_FOLDER, filename)
        reader = PdfReader(filepath)
        row_count = 0
        
        # 1. CHECK FOR "BLANK" IMAGE PDF
        sample_text = ""
        for i in range(min(3, len(reader.pages))):
            sample_text += (reader.pages[i].extract_text() or "")
            
        compressed_text = re.sub(r'\s+', '', sample_text.upper())
        
        # =========================================================================
        # METHOD 3: AI VISION OCR ENGINE (For Flipped Image Scans)
        # =========================================================================
        if len(compressed_text) < 50:
            print(f"\n[!] {filename}: No digital text found. Booting AI OCR...")
            
            try:
                images = convert_from_path(filepath)
                current_course = None
                
                # Progress bar for OCR Pages
                pbar = tqdm(images, desc=f"OCR {filename}", unit="page")
                for img in pbar:
                    fixed_img = img.rotate(180, expand=True)
                    text = pytesseract.image_to_string(fixed_img)
                    lines = text.split('\n')
                    
                    for idx, line in enumerate(lines):
                        line_str = line.strip().upper()
                        if not line_str: continue
                        
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
                        elif "UCE" in line_str or "UNIVERSITY COLLEGE" in line_str: col_code = "UCE"
                        elif "PRN" in line_str or "PERUMON" in line_str or "PAN |" in line_str: col_code = "PRN"
                        elif "AJC" in line_str or "AMAL JYOTHI" in line_str or "AC [" in line_str: col_code = "AJC"
                        elif "CEC" in line_str or "CHERTHALA" in line_str: col_code = "CEC"
                        else:
                            for code in KEAM_COLLEGES.keys():
                                if re.search(rf'\b{code}\b', line_str):
                                    col_code = code
                                    break
                                    
                        if col_code and current_course:
                            clean_college = KEAM_COLLEGES_FORMATTED[col_code]
                            data_pool = line_str
                            if idx + 1 < len(lines): data_pool += " " + lines[idx+1].strip()
                            
                            rank_tokens = re.findall(r'\b\d{4,5}\b', data_pool)
                            for c_idx, rank_str in enumerate(rank_tokens):
                                if c_idx < len(MATRIX_CATEGORIES):
                                    added = insert_record(cursor, year, phase, "CUTOFF", int(rank_str), MATRIX_CATEGORIES[c_idx], clean_college, current_course, "SM")
                                    row_count += added
                    
                    pbar.set_postfix(rows=row_count)
            except Exception as e:
                print(f"    [X] OCR Failed on {filename}: {e}")

        # =========================================================================
        # METHOD 1 & 2: DIGITAL TEXT PARSERS (Matrix / Line Engines)
        # =========================================================================
        else:
            is_cutoff_matrix = any(keyword in compressed_text for keyword in ["LASTRANK", "THEFOLLOWINGTABLE", "SMEZMU"])

            if is_cutoff_matrix:
                print(f"\n[+] Digital Matrix layout verified for {filename}.")
                current_course = None
                
                # Progress bar for Digital Pages
                pbar = tqdm(reader.pages, desc=f"Matrix parsing {filename}", unit="page")
                for page in pbar:
                    text = page.extract_text()
                    if not text: continue
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
                                if any(f" {c} " in f" {next_line} " for c in KEAM_COLLEGES) or ":" in next_line: break
                                data_pool += " " + next_line
                                look_ahead_idx += 1
                                
                            rank_tokens = [r for r in re.findall(r'\b\d+\b', data_pool) if int(r) != year and int(r) < 100000]
                            for c_idx, rank_str in enumerate(rank_tokens):
                                if c_idx < len(MATRIX_CATEGORIES):
                                    added = insert_record(cursor, year, phase, "CUTOFF", int(rank_str), MATRIX_CATEGORIES[c_idx], clean_college, current_course, "SM")
                                    row_count += added
                                    
                    pbar.set_postfix(rows=row_count)

            else:
                print(f"\n[+] Digital Individual layout verified for {filename}.")
                current_block = []
                
                def process_buffered_block(block_text):
                    nonlocal row_count
                    tokens = block_text.split()
                    app_no, rank, col_code, crs_code, seat_type = None, None, None, None, "SM"
                    
                    app_idx = -1
                    for i, t in enumerate(tokens):
                        clean_num = re.sub(r'\D', '', t)
                        if len(clean_num) in [6, 7]:
                            app_no = clean_num
                            app_idx = i
                            break
                    if not app_no: return
                    
                    for i in range(app_idx + 1, len(tokens)):
                        clean_rank = re.sub(r'[^0-9]', '', tokens[i])
                        if clean_rank:
                            rank = int(clean_rank)
                            break
                            
                    for t in tokens:
                        clean_alpha = re.sub(r'[^A-Z]', '', t.upper())
                        if len(clean_alpha) == 3 and clean_alpha in KEAM_COLLEGES_FORMATTED: col_code = clean_alpha
                        if len(clean_alpha) == 2 and clean_alpha in KEAM_COURSES_FORMATTED: crs_code = clean_alpha
                            
                    for t in reversed(tokens):
                        clean_alpha = re.sub(r'[^A-Z]', '', t.upper())
                        if 2 <= len(clean_alpha) <= 3 and clean_alpha not in [col_code, crs_code]:
                            if clean_alpha in MATRIX_CATEGORIES + ['FW', 'PT', 'MM', 'NCI', 'NRI', 'CC', 'CG', 'DK']:
                                seat_type = clean_alpha
                                break
                                
                    if app_no and rank and col_code and crs_code:
                        clean_college = KEAM_COLLEGES_FORMATTED[col_code]
                        clean_course = KEAM_COURSES_FORMATTED[crs_code]
                        added = insert_record(cursor, year, phase, app_no, rank, seat_type, clean_college, clean_course, seat_type)
                        row_count += added

                # Progress bar for Digital Pages
                pbar = tqdm(reader.pages, desc=f"Line parsing {filename}", unit="page")
                for page in pbar:
                    text = page.extract_text()
                    if not text: continue
                    lines = text.split('\n')
                    for line in lines:
                        line_str = line.strip()
                        if not line_str or any(h in line_str for h in ["SINo", "SI.No", "Office of the", "Date", "Page"]): continue
                        if re.search(r'\b\d{6,7}\b', line_str):
                            if current_block: process_buffered_block(" ".join(current_block))
                            current_block = [line_str]
                        else:
                            if current_block: current_block.append(line_str)
                    
                    pbar.set_postfix(rows=row_count)
                    
                if current_block: process_buffered_block(" ".join(current_block))

        conn.commit()
        
    conn.close()
    print("\n[+] Success! Your composite multiversion database is ready.")

if __name__ == "__main__":
    process_pdfs()
