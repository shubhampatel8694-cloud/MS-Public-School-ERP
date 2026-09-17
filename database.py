import psycopg2
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# 👇 अपना पूलर्स लिंक यहाँ डालें (पासवर्ड का @ %40 होना चाहिए)
DB_URI = "postgresql://postgres.bddsmybawhqwnleqtzsf:Msps%40larawak2026@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

# ==========================================
# 🪄 BULLETPROOF DATABASE & PANDAS BRIDGE
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

    def __getattr__(self, name):
        return getattr(self.cursor, name)

class DBConn:
    def __init__(self, uri):
        self.conn = psycopg2.connect(uri)
        self.conn.autocommit = True
        self.engine = create_engine(uri)

    def cursor(self):
        return DBCursor(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def __getattr__(self, name):
        return getattr(self.engine, name)

@st.cache_resource
def init_connection():
    return DBConn(DB_URI)

try:
    conn = init_connection()
    c = conn.cursor()
except Exception as e:
    st.error(f"Database Connection Failed: {e}")

# 🛡️ PANDAS KEY-ERROR FIXER (Auto-converts lowercase back to Title Case for UI)
_original_read_sql_query = pd.read_sql_query

def safe_read_sql_query(sql, con, params=None, *args, **kwargs):
    try:
        engine = getattr(con, 'engine', con)
        if isinstance(sql, str):
            pg_sql = sql.replace('?', '%s')
            df = pd.read_sql(text(pg_sql) if params else pg_sql, engine, params=params, *args, **kwargs)
        else:
            df = _original_read_sql_query(sql, con, params=params, *args, **kwargs)
        
        # जादुई डिक्शनरी: यह क्लाउड के नामों को वापस आपके पुराने ऐप वाले नामों में बदल देगी
        renames = {
            'roll_no': 'Roll No', 'receipt_no': 'Receipt No', 'sch_no': 'Sch No',
            'father_name': 'Father Name', 'mother_name': 'Mother Name', 'dob': 'DOB',
            'van_fee': 'Van Fee', 'eng_fee': 'Eng Fee', 'other_fee': 'Other Fee',
            'reg_fee': 'Reg Fee', 'adm_fee': 'Adm Fee', 'q_exam': 'Q Exam',
            'h_exam': 'H Exam', 'y_exam': 'Y Exam', 'item_name': 'Item Name',
            'collected_by': 'Collected By', 'ut1': 'UT1', 'ut2': 'UT2', 'hy': 'HY'
        }
        df.columns = [renames.get(col, col.title()) for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Pandas SQL Error: {e}")
        return pd.DataFrame()

pd.read_sql_query = safe_read_sql_query

# ==========================================
# 🚨 SMART SCHEMA RESET (Fixes the Name/Class Mix-up automatically)
# ==========================================
try:
    c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='student_master' AND ordinal_position=2")
    res = c.fetchone()
    if res and res[0] == 'sch_no':
        c.execute("DROP TABLE student_master") # पुराने गलत ढांचे को डिलीट करता है
except:
    pass

# ==========================================
# 🏗️ INITIALIZE CLOUD DATABASE TABLES (With Correct Column Order)
# ==========================================
c.execute('''CREATE TABLE IF NOT EXISTS student_master (
    roll_no INTEGER PRIMARY KEY,
    name TEXT,
    class TEXT,
    father_name TEXT,
    transport TEXT,
    medium TEXT,
    sch_no TEXT,
    mother_name TEXT,
    dob TEXT
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
# ⚙️ AUTO-HEAL & DEFAULT SETTINGS
# ==========================================
exam_list = ["UNIT TEST I", "HALF YEARLY EXAM", "UNIT TEST II", "ANNUAL EXAM"]

c_list = ["L.K.G", "U.K.G", "1", "2", "3", "4", "5", "6", "7", "8"]
for cls in c_list:
    c.execute("SELECT COUNT(*) FROM fee_structure WHERE class=?", (cls,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO fee_structure (class, reg_fee, adm_fee, tuition, q_exam, h_exam, y_exam, van_fee, eng_fee, other_fee) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0)", (cls,))

c.execute("SELECT DISTINCT class FROM student_master")
for row in c.fetchall():
    active_class = row[0]
    c.execute("SELECT COUNT(*) FROM fee_structure WHERE class=?", (active_class,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO fee_structure (class, reg_fee, adm_fee, tuition, q_exam, h_exam, y_exam, van_fee, eng_fee, other_fee) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0)", (active_class,))
        
conn.commit()