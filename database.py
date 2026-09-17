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

# 🛡️ BULLETPROOF PANDAS OVERRIDE (Handles all SQL types & parameters)
_original_read_sql_query = pd.read_sql_query

def safe_read_sql_query(sql, con, params=None, *args, **kwargs):
    try:
        # If connection is our custom DBConn, use its SQLAlchemy engine
        engine = getattr(con, 'engine', con)
        if isinstance(sql, str):
            pg_sql = sql.replace('?', '%s')
            return pd.read_sql(text(pg_sql) if params else pg_sql, engine, params=params, *args, **kwargs)
        return _original_read_sql_query(sql, con, params=params, *args, **kwargs)
    except Exception as e:
        try:
            # Fallback manual execution via psycopg2 cursor
            pg_query = sql.replace('?', '%s')
            cur = conn.cursor()
            if params:
                cur.execute(pg_query, params)
            else:
                cur.execute(pg_query)
            data = cur.fetchall()
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return pd.DataFrame(data, columns=columns)
        except Exception as ex:
            st.error(f"SQL Error: {ex}")
            return pd.DataFrame()

pd.read_sql_query = safe_read_sql_query

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
# ==========================================
# ⚙️ AUTO-HEAL & DEFAULT SETTINGS
# ==========================================
exam_list = ["UNIT TEST I", "HALF YEARLY EXAM", "UNIT TEST II", "ANNUAL EXAM"]

# 1. Default Classes
c_list = ["L.K.G", "U.K.G", "1", "2", "3", "4", "5", "6", "7", "8"]
for cls in c_list:
    c.execute("SELECT COUNT(*) FROM fee_structure WHERE class=?", (cls,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO fee_structure (class, reg_fee, adm_fee, tuition, q_exam, h_exam, y_exam, van_fee, eng_fee, other_fee) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0)", (cls,))

# 2. Auto-Heal Dynamic Classes (Prevents App Crash)
c.execute("SELECT DISTINCT class FROM student_master")
for row in c.fetchall():
    active_class = row[0]
    c.execute("SELECT COUNT(*) FROM fee_structure WHERE class=?", (active_class,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO fee_structure (class, reg_fee, adm_fee, tuition, q_exam, h_exam, y_exam, van_fee, eng_fee, other_fee) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0)", (active_class,))
        
conn.commit()