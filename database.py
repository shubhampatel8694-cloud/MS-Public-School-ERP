import psycopg2
import streamlit as st

# 👇 नीचे दी गई लाइन के अंदर अपना कॉपी किया हुआ Supabase URI लिंक पेस्ट करें
# [YOUR-PASSWORD] को मिटाकर अपना असली पासवर्ड लिखें (ब्रैकेट हटा दें)
DB_URI = "postgresql://postgres:Msps@larawak2026@db.bddsmybawhqwnleqtzsf.supabase.co:5432/postgres"

# ==========================================
# 🪄 MAGIC WRAPPER (SQLite to PostgreSQL Converter)
# ==========================================
class DBCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        pg_query = query.replace('?', '%s')
        if params:
            self.cursor.execute(pg_query, params)
        else:
            self.cursor.execute(pg_query)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

class DBConn:
    def __init__(self, uri):
        self.conn = psycopg2.connect(uri)
        self.conn.autocommit = True

    def cursor(self):
        return DBCursor(self.conn.cursor())

    def commit(self):
        self.conn.commit()

# Fast Cloud Connection
@st.cache_resource
def init_connection():
    return DBConn(DB_URI)

try:
    conn = init_connection()
    c = conn.cursor()
except Exception as e:
    st.error(f"Database Connection Failed: {e}")

# ==========================================
# 🏗️ INITIALIZE CLOUD DATABASE TABLES
# ==========================================
c.execute('''CREATE TABLE IF NOT EXISTS student_master (
    roll_no INTEGER PRIMARY KEY,
    sch_no TEXT,
    name TEXT,
    class TEXT,
    father_name TEXT,
    mother_name TEXT,
    dob TEXT,
    transport TEXT,
    medium TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS fee_structure (
    class TEXT PRIMARY KEY,
    reg_fee INTEGER,
    adm_fee INTEGER,
    tuition INTEGER,
    q_exam INTEGER,
    h_exam INTEGER,
    y_exam INTEGER,
    van_fee INTEGER,
    eng_fee INTEGER,
    other_fee INTEGER
)''')

c.execute('''CREATE TABLE IF NOT EXISTS fee_log (
    receipt_no TEXT PRIMARY KEY,
    date TEXT,
    roll_no INTEGER,
    amount INTEGER,
    mode TEXT,
    head TEXT,
    collected_by TEXT
)''')

# PostgreSQL uses SERIAL for auto-increment IDs
c.execute('''CREATE TABLE IF NOT EXISTS student_charges (
    id SERIAL PRIMARY KEY,
    roll_no INTEGER,
    item_name TEXT,
    amount INTEGER,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS marks_entry (
    id SERIAL PRIMARY KEY,
    roll_no INTEGER,
    subject TEXT,
    ut1 INTEGER,
    hy INTEGER,
    ut2 INTEGER,
    annual INTEGER
)''')

c.execute('''CREATE TABLE IF NOT EXISTS admit_timetable (
    class TEXT,
    exam_name TEXT,
    time_slot TEXT,
    d1 TEXT, s1 TEXT, d2 TEXT, s2 TEXT, d3 TEXT, s3 TEXT, d4 TEXT, s4 TEXT, d5 TEXT, s5 TEXT,
    d6 TEXT, s6 TEXT, d7 TEXT, s7 TEXT, d8 TEXT, s8 TEXT, d9 TEXT, s9 TEXT, d10 TEXT, s10 TEXT
)''')

# ==========================================
# ⚙️ DEFAULT SETTINGS
# ==========================================
c_list = ["L.K.G", "U.K.G", "1", "2", "3", "4", "5", "6", "7", "8"]
exam_list = ["UNIT TEST I", "HALF YEARLY EXAM", "UNIT TEST II", "ANNUAL EXAM"]

c.execute("SELECT COUNT(*) FROM fee_structure")
if c.fetchone()[0] == 0:
    for cls in c_list:
        c.execute("INSERT INTO fee_structure (class, reg_fee, adm_fee, tuition, q_exam, h_exam, y_exam, van_fee, eng_fee, other_fee) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0)", (cls,))
    conn.commit()