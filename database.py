import sqlite3

# --- DATABASE SETUP ---
conn = sqlite3.connect('ms_school.db', check_same_thread=False)
c = conn.cursor()

c_list = ["NUR", "L.K.G", "U.K.G"] + [str(i) for i in range(1, 13)]

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS student_master (roll_no INTEGER PRIMARY KEY, name TEXT, class TEXT, father_name TEXT, transport TEXT, medium TEXT)''')
    try: c.execute("ALTER TABLE student_master ADD COLUMN mother_name TEXT DEFAULT ''")
    except: pass
    try: c.execute("ALTER TABLE student_master ADD COLUMN dob TEXT DEFAULT ''")
    except: pass
    try: c.execute("ALTER TABLE student_master ADD COLUMN sch_no TEXT DEFAULT ''")
    except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS fee_log (receipt_no TEXT PRIMARY KEY, date TEXT, roll_no INTEGER, amount INTEGER, mode TEXT, head TEXT)''')
    try: c.execute("ALTER TABLE fee_log ADD COLUMN collected_by TEXT DEFAULT 'Main Admin'")
    except: pass

    c.execute('''CREATE TABLE IF NOT EXISTS fee_structure (class TEXT PRIMARY KEY, reg_fee INTEGER, adm_fee INTEGER, tuition INTEGER, q_exam INTEGER, h_exam INTEGER, y_exam INTEGER, van_fee INTEGER, eng_fee INTEGER, other_fee INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS student_charges (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no INTEGER, item_name TEXT, amount INTEGER, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS marks_entry (id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no INTEGER, subject TEXT, ut1 INTEGER, hy INTEGER, ut2 INTEGER, annual INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admit_timetable (class TEXT, exam_name TEXT, time_slot TEXT, d1 TEXT, s1 TEXT, d2 TEXT, s2 TEXT, d3 TEXT, s3 TEXT, d4 TEXT, s4 TEXT, d5 TEXT, s5 TEXT, d6 TEXT, s6 TEXT, d7 TEXT, s7 TEXT, d8 TEXT, s8 TEXT, d9 TEXT, s9 TEXT, d10 TEXT, s10 TEXT, PRIMARY KEY(class, exam_name))''')
    conn.commit()

    c.execute("SELECT COUNT(*) FROM fee_structure")
    if c.fetchone()[0] == 0:
        for cls in c_list: 
            c.execute("INSERT INTO fee_structure VALUES (?, 100, 1000, 250, 150, 250, 300, 300, 100, 100)", (cls,))
        conn.commit()

# Run this setup immediately when the file is imported
init_db()