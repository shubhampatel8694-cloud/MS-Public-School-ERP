import os
import base64
from datetime import datetime
import streamlit as st
from database import c, c_list

# --- SETTINGS ---
ADMIN_USERS = {
    "9455587731": "Msps&@7731",
    "admin2": "1234",   
    "admin3": "1234"    
}
exam_list = ["QUARTERLY EXAM", "HALF-YEARLY EXAM", "YEARLY EXAM", "YEARLY EXAMINATION 2026"]

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return ""

LOGO_BASE64 = get_base64_image("msps png.png")

# --- FUNCTIONS ---
def get_current_m_idx():
    m = datetime.today().month
    return m - 3 if m >= 4 else m + 9

def get_next_receipt_no():
    c.execute("SELECT receipt_no FROM fee_log ORDER BY receipt_no DESC LIMIT 1")
    last = c.fetchone()
    if last and last[0].startswith("REC-"):
        try: return f"REC-{int(last[0].split('-')[1])+1:05d}"
        except: pass
    return "REC-00001"

def get_student_financials(roll, current_m_idx):
    c.execute("SELECT * FROM student_master WHERE roll_no=?", (roll,))
    stu = c.fetchone()
    if not stu: return 0, 0, 0, 0, None
    cls, transport, medium = stu[2], stu[4], stu[5]
    c.execute("SELECT * FROM fee_structure WHERE class=?", (cls,))
    fs = c.fetchone()
    payable = fs[1] + fs[2] + fs[9] + (fs[3] * current_m_idx) 
    if current_m_idx >= 4: payable += fs[4] 
    if current_m_idx >= 7: payable += fs[5]
    if current_m_idx >= 12: payable += fs[6]
    if transport == "Van": payable += (fs[7] * current_m_idx)
    if medium == "ENGLISH": payable += (fs[8] * current_m_idx)
    c.execute("SELECT SUM(amount) FROM student_charges WHERE roll_no=?", (roll,))
    payable += (c.fetchone()[0] or 0)
    c.execute("SELECT SUM(amount) FROM fee_log WHERE roll_no=?", (roll,))
    paid = c.fetchone()[0] or 0
    return payable, paid, max(0, payable - paid), max(0, paid - payable), stu

def get_grade(total_100):
    if total_100 >= 91: return "A1"
    elif total_100 >= 81: return "A2"
    elif total_100 >= 71: return "B1"
    elif total_100 >= 61: return "B2"
    elif total_100 >= 51: return "C1"
    elif total_100 >= 41: return "C2"
    elif total_100 >= 33: return "D"
    else: return "E (FAIL)"

def force_rerun():
    try: st.rerun()
    except AttributeError: st.experimental_rerun()

def format_date(d_str):
    try: return datetime.strptime(d_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    except: return d_str

def get_subjects_for_class(cls):
    if cls in ["NUR", "L.K.G", "U.K.G"]: return ["HINDI", "ENGLISH", "MATH", "ART", "PHYSICAL", "ORAL"]
    elif cls in ["1", "2", "3", "4", "5"]: return ["HINDI", "SCIENCE", "ENGLISH", "MATH", "SANSKRIT", "OUR SOCIETY", "MORAL EDU & PHYSICAL", "ART & ORAL"]
    elif cls in ["6", "7", "8"]: return ["HINDI", "SCIENCE", "ENGLISH", "MATH", "SANSKRIT", "SOCIAL SCIENCE", "AGRICULTURE & PHYSICAL", "ART & ORAL"]
    elif cls in ["9", "10"]: return ["HINDI", "SCIENCE", "SOCIAL SCIENCE", "ENGLISH", "MATH/H.SCIENCE", "ART", "COMPUTER"]
    elif cls in ["11", "12"]: return ["HINDI", "GEN. HINDI", "ENGLISH", "PHYSICS", "CHEMISTRY", "BIOLOGY", "MATH", "SOCIOLOGY", "HOME SCIENCE", "HISTORY", "SANSKRIT", "ART", "GEOGRAPHY", "ECONOMICS", "CIVICS"]
    return ["HINDI", "ENGLISH", "MATH"]