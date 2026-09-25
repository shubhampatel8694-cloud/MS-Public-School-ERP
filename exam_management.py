import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from database import conn, c, c_list
from helpers import *

def get_dynamic_subjects(cls_name, medium):
    try:
        c.execute("SELECT subject_name FROM class_subjects WHERE class_name=? AND medium=? ORDER BY id", (cls_name, medium))
        subs = [r[0] for r in c.fetchall()]
        return subs if subs else []
    except:
        return []

def get_custom_grade(marks):
    if marks >= 90: return "A"
    elif marks >= 75: return "B"
    else: return "C"

def show_exam_management():
    st.markdown('''<style>
        div[data-baseweb="input"] input, div[data-baseweb="select"] span {
            color: #000000 !important;
            font-weight: 600 !important;
        }
    </style>''', unsafe_allow_html=True)

    if 'admit_preview' not in st.session_state: st.session_state.admit_preview = None
    if 'report_preview' not in st.session_state: st.session_state.report_preview = None

    role = st.session_state.get('role')
    
    if role == 'Teacher':
        exam_menu = st.sidebar.radio("Teacher Exam Menu", ["📝 Bulk Marks Entry"])
    else:
        exam_menu = st.sidebar.radio("Exam Menu", ["🎯 Exam Dashboard", "📚 Subject Master", "📅 Setup Admit Card", "📝 Bulk Marks Entry", "🖨️ Print Admit Card", "📄 Print Report Card"])
    
    # ==========================================
    # 1. EXAM DASHBOARD
    # ==========================================
    if exam_menu == "🎯 Exam Dashboard":
        st.subheader("Welcome to M.S. Public School Exam Module!")
        c.execute("SELECT COUNT(DISTINCT roll_no) FROM marks_entry")
        marks_entered = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM student_master")
        tot_students = c.fetchone()[0] or 0
        
        c1, c2 = st.columns(2)
        c1.metric("👥 Total Students", f"{tot_students}")
        c2.metric("📝 Students with Marks Entered", f"{marks_entered}")

    # ==========================================
    # 2. 📚 SUBJECT MASTER
    # ==========================================
    elif exam_menu == "📚 Subject Master":
        st.subheader("Add or Delete Subjects for Classes")
        col1, col2 = st.columns(2)
        s_cls = col1.selectbox("Select Class", c_list, key="sub_cls")
        s_med = col2.selectbox("Select Medium", ["Hindi", "English"], key="sub_med")
        
        c.execute("SELECT subject_name FROM class_subjects WHERE class_name=? AND medium=? ORDER BY id", (s_cls, s_med))
        existing_subs = [r[0] for r in c.fetchall()]
        
        st.write("---")
        c_add, c_del = st.columns(2)
        
        with c_add:
            st.markdown("#### ➕ Add New Subject")
            new_sub = st.text_input("Enter Subject Name (e.g. MATHS, HINDI)")
            if st.button("💾 Save Subject"):
                if new_sub:
                    c.execute("INSERT INTO class_subjects (class_name, medium, subject_name) VALUES (?, ?, ?)", (s_cls, s_med, new_sub.upper()))
                    conn.commit(); st.success(f"{new_sub.upper()} added to {s_cls} ({s_med})!"); force_rerun()
                else:
                    st.warning("Please enter a subject name!")
                    
        with c_del:
            st.markdown("#### 🗑️ Delete Subject")
            if existing_subs:
                del_sub = st.selectbox("Select Subject to Delete", existing_subs)
                if st.button("❌ Delete Selected"):
                    c.execute("DELETE FROM class_subjects WHERE class_name=? AND medium=? AND subject_name=?", (s_cls, s_med, del_sub))
                    conn.commit(); st.error(f"{del_sub} deleted!"); force_rerun()
            else:
                st.info(f"No subjects found for Class {s_cls} ({s_med})")

    # ==========================================
    # 3. SETUP ADMIT CARD TIMETABLE
    # ==========================================
    elif exam_menu == "📅 Setup Admit Card":
        st.subheader("Set Class-wise Admit Card Timetable")
        colA, colB, colC, colD = st.columns(4)
        tt_cls = colA.selectbox("Select Class", c_list)
        tt_med = colB.selectbox("Select Medium", ["Hindi", "English"])
        tt_exam = colC.selectbox("Select Exam", exam_list)
        
        c.execute("SELECT time_slot, d1, s1, d2, s2, d3, s3, d4, s4, d5, s5, d6, s6, d7, s7, d8, s8, d9, s9, d10, s10 FROM admit_timetable WHERE class=? AND medium=? AND exam_name=?", (tt_cls, tt_med, tt_exam))
        ext = c.fetchone()
        if not ext:
            c.execute("SELECT time_slot, d1, s1, d2, s2, d3, s3, d4, s4, d5, s5, d6, s6, d7, s7, d8, s8, d9, s9, d10, s10 FROM admit_timetable WHERE class=? AND exam_name=? LIMIT 1", (tt_cls, tt_exam))
            ext = c.fetchone()
            
        tt_time = colD.text_input("Time Slot", value=ext[0] if ext else "10:30 AM - 01:30 PM")
        
        st.write("---")
        st.markdown("### 📝 Enter Dates & Subjects")
        
        d_vals = [datetime.today().date()] * 10
        s_vals = ["---"] * 10
        if ext:
            for i in range(10):
                try: d_vals[i] = datetime.strptime(ext[1 + i*2], "%Y-%m-%d").date()
                except: pass
                if ext[2 + i*2]: s_vals[i] = ext[2 + i*2]
        
        db_subs = get_dynamic_subjects(tt_cls, tt_med)
        if not db_subs:
            db_subs = get_subjects_for_class(tt_cls)
            
        base_subs = ["---"]
        for s in db_subs:
            if s not in base_subs: base_subs.append(s)
            
        for s in s_vals:
            if s and s != "---" and s not in base_subs:
                base_subs.append(s)
                
        def safe_idx(val): return base_subs.index(val) if val in base_subs else 0

        with st.form("timetable_form"):
            c1, c2, c3, c4 = st.columns(4)
            d1 = c1.date_input("Date 1", value=d_vals[0]); s1 = c2.selectbox("Sub 1", base_subs, index=safe_idx(s_vals[0]))
            d6 = c3.date_input("Date 6", value=d_vals[5]); s6 = c4.selectbox("Sub 6", base_subs, index=safe_idx(s_vals[5]))
            d2 = c1.date_input("Date 2", value=d_vals[1]); s2 = c2.selectbox("Sub 2", base_subs, index=safe_idx(s_vals[1]))
            d7 = c3.date_input("Date 7", value=d_vals[6]); s7 = c4.selectbox("Sub 7", base_subs, index=safe_idx(s_vals[6]))
            d3 = c1.date_input("Date 3", value=d_vals[2]); s3 = c2.selectbox("Sub 3", base_subs, index=safe_idx(s_vals[2]))
            d8 = c3.date_input("Date 8", value=d_vals[7]); s8 = c4.selectbox("Sub 8", base_subs, index=safe_idx(s_vals[7]))
            d4 = c1.date_input("Date 4", value=d_vals[3]); s4 = c2.selectbox("Sub 4", base_subs, index=safe_idx(s_vals[3]))
            d9 = c3.date_input("Date 9", value=d_vals[8]); s9 = c4.selectbox("Sub 9", base_subs, index=safe_idx(s_vals[8]))
            d5 = c1.date_input("Date 5", value=d_vals[4]); s5 = c2.selectbox("Sub 5", base_subs, index=safe_idx(s_vals[4]))
            d10 = c3.date_input("Date 10", value=d_vals[9]); s10 = c4.selectbox("Sub 10", base_subs, index=safe_idx(s_vals[9]))

            submit_btn = st.form_submit_button("💾 Save Timetable for this Class")
            
            if submit_btn:
                c.execute("DELETE FROM admit_timetable WHERE class=? AND exam_name=?", (tt_cls, tt_exam))
                c.execute("""INSERT INTO admit_timetable 
                          (class, medium, exam_name, time_slot, d1, s1, d2, s2, d3, s3, d4, s4, d5, s5, d6, s6, d7, s7, d8, s8, d9, s9, d10, s10) 
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                          (tt_cls, tt_med, tt_exam, tt_time, str(d1), s1, str(d2), s2, str(d3), s3, str(d4), s4, str(d5), s5, str(d6), s6, str(d7), s7, str(d8), s8, str(d9), s9, str(d10), s10))
                conn.commit()
                st.success(f"✅ Timetable Saved for Class {tt_cls} ({tt_med})!")

    # ==========================================
    # 4. BULK MARKS ENTRY (🔥 FIX: EXCEL STYLE TEXT INPUTS)
    # ==========================================
    elif exam_menu == "📝 Bulk Marks Entry":
        st.subheader("✏️ Batch Marks Entry")
        col1, col2, col3 = st.columns(3)
        m_cls = col1.selectbox("Select Class", c_list)
        m_med = col2.selectbox("Select Medium", ["Hindi", "English"])
        
        cls_subjects = get_dynamic_subjects(m_cls, m_med)
        if not cls_subjects:
            cls_subjects = get_subjects_for_class(m_cls)
            
        m_sub = col3.selectbox("Select Subject", cls_subjects)

        c.execute("SELECT roll_no, name, class, medium FROM student_master ORDER BY roll_no")
        all_students_db = c.fetchall()
        
        students = []
        for s_roll, s_name, s_cls, s_md in all_students_db:
            clean_cls = s_cls.upper().replace("(HINDI)", "").replace("(ENGLISH)", "").strip()
            chk_med = s_md if s_md else "Hindi"
            if clean_cls == m_cls.upper() and chk_med.upper() == m_med.upper():
                students.append((s_roll, s_name))

        if students:
            with st.form("marks_entry_form"):
                st.markdown(f"### 📊 Enter Marks for **{m_sub}** ({m_cls})")
                st.info("💡 Aaram se sabhi bacchon ke number bhariye. Jab sab bhar jayein, tab neeche 'Save All Marks' button dabayein.")
                
                h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 2])
                h1.markdown("**🧑‍🎓 Student Details**")
                h2.markdown("**UT1**")
                h3.markdown("**Half Yearly**")
                h4.markdown("**UT2**")
                h5.markdown("**Annual**")
                st.markdown("---")
                
                input_data = []
                for roll, name in students:
                    c.execute("SELECT ut1, hy, ut2, annual FROM marks_entry WHERE roll_no=? AND subject=?", (roll, m_sub))
                    existing = c.fetchone()
                    e_u1, e_h, e_u2, e_a = existing if existing else (0, 0, 0, 0)
                    
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                    
                    c1.markdown(f"<div style='padding-top:8px; font-size:14px;'><b>{roll}</b> - {name.upper()}</div>", unsafe_allow_html=True)
                    
                    # 🔥 FIX: TEXT INPUT for clean typing without bounce-backs!
                    u1 = c2.text_input("U1", value=str(int(e_u1)), key=f"u1_{roll}", label_visibility="collapsed")
                    h = c3.text_input("HY", value=str(int(e_h)), key=f"hy_{roll}", label_visibility="collapsed")
                    u2 = c4.text_input("U2", value=str(int(e_u2)), key=f"u2_{roll}", label_visibility="collapsed")
                    a = c5.text_input("AN", value=str(int(e_a)), key=f"an_{roll}", label_visibility="collapsed")
                    
                    input_data.append((roll, u1, h, u2, a))
                    
                st.markdown("---")
                if st.form_submit_button(f"💾 Save All Marks for {m_sub}", use_container_width=True):
                    for r_no, u1_val, h_val, u2_val, a_val in input_data:
                        # String se safely integer banana, agar khali ho to 0 maan lena
                        ut1 = int(u1_val) if str(u1_val).strip().isdigit() else 0
                        hy = int(h_val) if str(h_val).strip().isdigit() else 0
                        ut2 = int(u2_val) if str(u2_val).strip().isdigit() else 0
                        ann = int(a_val) if str(a_val).strip().isdigit() else 0
                        
                        c.execute("SELECT id FROM marks_entry WHERE roll_no=? AND subject=?", (r_no, m_sub))
                        if c.fetchone(): 
                            c.execute("UPDATE marks_entry SET ut1=?, hy=?, ut2=?, annual=? WHERE roll_no=? AND subject=?", (ut1, hy, ut2, ann, r_no, m_sub))
                        else: 
                            c.execute("INSERT INTO marks_entry (roll_no, subject, ut1, hy, ut2, annual) VALUES (?, ?, ?, ?, ?, ?)", (r_no, m_sub, ut1, hy, ut2, ann))
                    conn.commit()
                    st.success("✅ All Marks Saved Successfully!")
        else: 
            st.warning("⚠️ No students found in this class and medium.")

    # ==========================================
    # 5. PRINT ADMIT CARD
    # ==========================================
    elif exam_menu == "🖨️ Print Admit Card":
        st.subheader("Generate Hagaki (100x148mm) Admit Card")
        
        if st.session_state.admit_preview:
            mode, val1, exam_sel = st.session_state.admit_preview
            st.markdown("### 🖨️ Admit Card Print View")
            if st.button("❌ Close Preview & Go Back"):
                st.session_state.admit_preview = None; force_rerun()
            
            logo_tag = f'<img src="{LOGO_BASE64}" style="width: 65px; position: absolute; top: 8px; left: 12px;">' if LOGO_BASE64 else ''
            watermark = f'<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.1; z-index: -1;"><img src="{LOGO_BASE64}" style="width: 240px;"></div>' if LOGO_BASE64 else ''
            def fd(d_str, s_str): return format_date(d_str) if s_str != "---" else ""
            def fs(s_str): return s_str if s_str != "---" else "-"
            students_to_print = []
            
            if mode == "SINGLE":
                c.execute("SELECT roll_no, name, class, father_name, medium FROM student_master WHERE roll_no=?", (val1,))
                stu = c.fetchone()
                if stu: students_to_print.append(stu)
            else:
                c.execute("SELECT roll_no, name, class, father_name, medium FROM student_master ORDER BY roll_no")
                all_stu = c.fetchall()
                for s in all_stu:
                    cl_cln = s[2].upper().replace("(HINDI)", "").replace("(ENGLISH)", "").strip()
                    if cl_cln == val1.upper(): students_to_print.append(s)

            if not students_to_print: st.error("No students found!")
            else:
                all_cards_html = ""
                for stu_item in students_to_print:
                    r_num, s_name, s_class, f_name, s_med = stu_item
                    if not s_med: s_med = "Hindi" 
                    
                    display_cls = s_class.upper().replace("(HINDI)", "").replace("(ENGLISH)", "").strip()
                    
                    c.execute("SELECT time_slot, d1, s1, d2, s2, d3, s3, d4, s4, d5, s5, d6, s6, d7, s7, d8, s8, d9, s9, d10, s10 FROM admit_timetable WHERE class=? AND medium=? AND exam_name=?", (display_cls, s_med, exam_sel))
                    tt = c.fetchone()
                    if not tt: 
                        c.execute("SELECT time_slot, d1, s1, d2, s2, d3, s3, d4, s4, d5, s5, d6, s6, d7, s7, d8, s8, d9, s9, d10, s10 FROM admit_timetable WHERE class=? AND exam_name=? LIMIT 1", (display_cls, exam_sel))
                        tt = c.fetchone()
                        
                    if not tt: tt = ["10:30 AM - 01:30 PM", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---"]

                    all_cards_html += f"""
                    <div class="card-container">
                        {watermark} {logo_tag}
                        <div class="header-table">
                            <h1>M.S. PUBLIC SCHOOL</h1>
                            <h3>{exam_sel}</h3>
                            <h4>ADMIT CARD</h4>
                        </div>
                        <table class="info-table">
                            <tr>
                                <td class="lbl">NAME :</td><td class="val">{s_name.upper()}</td>
                                <td class="lbl" style="width: 15%; text-align: right;">ROLL NO :&nbsp;&nbsp;</td><td class="val" style="width: 15%; color: #000;">{r_num}</td>
                            </tr>
                            <tr><td class="lbl">FATHER'S NAME :</td><td class="val" colspan="3">{f_name.upper()}</td></tr>
                            <tr>
                                <td class="lbl">CLASS :</td><td class="val">{display_cls}</td>
                                <td colspan="2" style="text-align: right; vertical-align: bottom;">
                                    <div style="border-top: 1.5px solid #000; padding-top: 2px; font-size: 11px; color: #000; font-weight: bold; width: 160px; float: right; text-align: center;">PRINCIPAL'S SIGNATURE</div>
                                </td>
                            </tr>
                        </table>
                        <div class="time-lbl">TIME - ({tt[0]})</div>
                        <table class="tt-table">
                            <tr style="background-color: #E6F0FA;"><th>DAY</th><th>SUBJECT</th><th>DAY</th><th>SUBJECT</th></tr>
                            <tr><td>{fd(tt[1], tt[2])}</td><td>{fs(tt[2])}</td><td>{fd(tt[11], tt[12])}</td><td>{fs(tt[12])}</td></tr>
                            <tr><td>{fd(tt[3], tt[4])}</td><td>{fs(tt[4])}</td><td>{fd(tt[13], tt[14])}</td><td>{fs(tt[14])}</td></tr>
                            <tr><td>{fd(tt[5], tt[6])}</td><td>{fs(tt[6])}</td><td>{fd(tt[15], tt[16])}</td><td>{fs(tt[16])}</td></tr>
                            <tr><td>{fd(tt[7], tt[8])}</td><td>{fs(tt[8])}</td><td>{fd(tt[17], tt[18])}</td><td>{fs(tt[18])}</td></tr>
                            <tr><td>{fd(tt[9], tt[10])}</td><td>{fs(tt[10])}</td><td>{fd(tt[19], tt[20])}</td><td>{fs(tt[20])}</td></tr>
                        </table>
                    </div>
                    """
                final_html = f"""<html><head><style>body {{ font-family: 'Calibri', Arial, sans-serif; font-size: 11px; margin: 0; padding: 0; background: #fff; }} .card-container {{ width: 140mm; height: 94mm; margin: 10px auto; border: 2px solid #1F497D; padding: 8px 14px; position: relative; box-sizing: border-box; background: white; overflow: hidden; }} .header-table {{ width: 100%; border-collapse: collapse; text-align: center; margin-bottom: 6px; }} .header-table h1 {{ color: #FF0000; margin: 0; font-size: 23px; font-family: 'Times New Roman', serif; }} .header-table h3 {{ color: #000; margin: 2px 0; font-size: 13px; text-transform: uppercase; }} .header-table h4 {{ color: #0000FF; margin: 0; text-decoration: underline; font-size: 13px; }} .info-table {{ width: 100%; border-collapse: collapse; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; }} .info-table td {{ padding: 2px 0; }} .lbl {{ color: #000; width: 22%; }} .val {{ color: #0000FF; width: 48%; }} .time-lbl {{ color: #FF0000; font-weight: bold; font-size: 12px; margin-bottom: 2px; }} .tt-table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 11px; }} .tt-table th, .tt-table td {{ border: 1px solid #1F497D; padding: 4px; font-weight: bold; }} @media print {{ @page {{ size: 148mm 100mm landscape; margin: 2mm; }} body {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} .card-container {{ width: 100%; height: 96mm; margin: 0; border: 2px solid #1F497D; page-break-after: always; }} }}</style></head><body onload="setTimeout(() => window.print(), 500)">{all_cards_html}</body></html>"""
                components.html(final_html, height=650, scrolling=True)
                st.write("---"); st.stop()

        tab1, tab2 = st.tabs(["👤 Print Single Student", "🏫 Print Entire Class (Batch)"])
        with tab1:
            col1, col2 = st.columns(2)
            p_roll = col1.number_input("Enter Roll No", min_value=1, step=1)
            p_exam = col2.selectbox("Select Exam", exam_list, key="single_admit_ex")
            if st.button("Generate Single Admit Card"):
                c.execute("SELECT name FROM student_master WHERE roll_no=?", (p_roll,))
                if c.fetchone(): st.session_state.admit_preview = ("SINGLE", p_roll, p_exam); force_rerun()
                else: st.error("Roll No not found!")
        with tab2:
            colA, colB = st.columns(2)
            b_cls = colA.selectbox("Select Class to Print All", c_list, key="batch_admit_cls")
            b_exam = colB.selectbox("Select Exam", exam_list, key="batch_admit_ex")
            if st.button("Generate Class Admit Cards"):
                c.execute("SELECT COUNT(*) FROM student_master WHERE class LIKE ?", (f"{b_cls}%",))
                if c.fetchone()[0] > 0: st.session_state.admit_preview = ("BATCH", b_cls, b_exam); force_rerun()
                else: st.error("No students found in this class!")

    # ==========================================
    # 6. PRINT REPORT CARD
    # ==========================================
    elif exam_menu == "📄 Print Report Card":
        st.subheader("Generate Full A4 Report Card")
        
        with st.expander("⚙️ Report Card Form Settings", expanded=True):
            st.markdown("Select additional details (from admission) to show on the report card:")
            sel_fields = st.multiselect(
                "Click below to Add/Remove Fields:", 
                ["FATHER'S NAME", "MOTHER'S NAME", "DOB", "SCH NO", "TRANSPORT", "MEDIUM"], 
                default=["FATHER'S NAME", "MOTHER'S NAME", "DOB", "SCH NO"]
            )
            st.info("💡 Note: Missing subjects on the card? Please generate and 'Save' the Admit Card for that class first!")
            
        if st.session_state.report_preview:
            prev_data = st.session_state.report_preview
            mode = prev_data["mode"]
            val1 = prev_data["val1"]
            fields = prev_data["fields"]
            
            st.markdown("### 🖨️ A4 Report Card Print View")
            if st.button("❌ Close Preview & Go Back"):
                st.session_state.report_preview = None; force_rerun()
                
            students_to_print = []
            if mode == "SINGLE":
                c.execute("SELECT roll_no, name, class, father_name, mother_name, dob, sch_no, medium, transport FROM student_master WHERE roll_no=?", (val1,))
                stu = c.fetchone()
                if stu: students_to_print.append(stu)
            else:
                c.execute("SELECT roll_no, name, class, father_name, mother_name, dob, sch_no, medium, transport FROM student_master ORDER BY roll_no")
                all_stu = c.fetchall()
                for s in all_stu:
                    cl_cln = s[2].upper().replace("(HINDI)", "").replace("(ENGLISH)", "").strip()
                    if cl_cln == val1.upper(): students_to_print.append(s)

            if not students_to_print: st.error("No students found!")
            else:
                all_reports_html = ""
                for stu_item in students_to_print:
                    r_num, s_name, s_class, f_name, m_name, s_dob, s_sch, s_med, s_trans = stu_item
                    if not s_med: s_med = "Hindi"
                    if not s_trans: s_trans = "N/A"
                    
                    display_cls = s_class.upper().replace("(HINDI)", "").replace("(ENGLISH)", "").strip()
                    
                    student_data = {
                        "FATHER'S NAME": f_name.upper() if f_name else "",
                        "MOTHER'S NAME": m_name.upper() if m_name else "",
                        "DOB": s_dob if s_dob else "",
                        "SCH NO": s_sch if s_sch else "",
                        "TRANSPORT": s_trans.upper(),
                        "MEDIUM": s_med.upper()
                    }

                    info_rows = []
                    info_rows.append(f"<tr><td style='width: 15%;'>NAME</td><td style='width: 45%;'>: {s_name.upper()}</td><td style='width: 15%;'>CLASS</td><td style='width: 25%;'>: {display_cls}</td></tr>")
                    
                    dyn_col1 = []
                    dyn_col2 = [("ROLL NO", r_num)]
                    
                    for idx, field in enumerate(fields):
                        if idx % 2 == 0:
                            dyn_col1.append((field, student_data.get(field, "")))
                        else:
                            dyn_col2.append((field, student_data.get(field, "")))
                            
                    max_len = max(len(dyn_col1), len(dyn_col2))
                    for i in range(max_len):
                        c1_lbl, c1_val = dyn_col1[i] if i < len(dyn_col1) else ("", "")
                        c2_lbl, c2_val = dyn_col2[i] if i < len(dyn_col2) else ("", "")
                        c1_html = f"<td>{c1_lbl}</td><td>{': ' + str(c1_val) if c1_lbl else ''}</td>"
                        c2_html = f"<td>{c2_lbl}</td><td>{': ' + str(c2_val) if c2_lbl else ''}</td>"
                        info_rows.append(f"<tr>{c1_html}{c2_html}</tr>")
                        
                    info_table_html = f'<table class="info-table">{"".join(info_rows)}</table>'

                    c.execute("SELECT s1, s2, s3, s4, s5, s6, s7, s8, s9, s10 FROM admit_timetable WHERE class=? ORDER BY exam_name DESC LIMIT 1", (display_cls,))
                    tt_subs = c.fetchone()
                    if tt_subs:
                        ordered_subjects = [s for s in tt_subs if s and s != "---"]
                    else:
                        ordered_subjects = get_dynamic_subjects(display_cls, s_med)
                        if not ordered_subjects: ordered_subjects = get_subjects_for_class(display_cls)

                    marks_html = ""
                    t_ut1 = t_hy = t_ut2 = t_ann = t_grand = 0
                    t_hy_obt = t_hy_max = t_ann_obt = t_ann_max = t_grand_obt = t_grand_max = 0
                    
                    for subj in ordered_subjects:
                        c.execute("SELECT ut1, hy, ut2, annual FROM marks_entry WHERE roll_no=? AND subject=?", (r_num, subj))
                        res = c.fetchone()
                        u1, h, u2, a = res if res else (0, 0, 0, 0)
                        
                        if display_cls in ["5", "8"]:
                            row_tot = u1 + h + u2 + a
                            grade = get_custom_grade(row_tot)
                            t_ut1+=u1; t_hy+=h; t_ut2+=u2; t_ann+=a; t_grand+=row_tot
                            marks_html += f"<tr><td style='text-align: left; padding-left: 10px;'>{subj}</td><td>{u1}</td><td>{h}</td><td>{u2}</td><td>{a}</td><td>{row_tot}</td><td>{grade}</td></tr>"
                        
                        elif display_cls in ["6", "7"]:
                            max_m = 100 if subj.upper() in ["HINDI", "MATH", "SOCIAL SCIENCE", "AGRICULTURE", "MATHEMATICS"] else 50
                            row_tot_obt = h + a
                            row_tot_max = max_m * 2
                            pct = (row_tot_obt / row_tot_max) * 100 if row_tot_max > 0 else 0
                            grade = get_custom_grade(pct)
                            t_hy_obt+=h; t_hy_max+=max_m; t_ann_obt+=a; t_ann_max+=max_m
                            t_grand_obt+=row_tot_obt; t_grand_max+=row_tot_max
                            marks_html += f"<tr><td style='text-align: left; padding-left: 10px;'>{subj}</td><td>{h}</td><td>{max_m}</td><td>{a}</td><td>{max_m}</td><td>{row_tot_obt}</td><td>{row_tot_max}</td><td>{grade}</td></tr>"

                        else:
                            row_tot = h + a
                            pct = (row_tot / 100) * 100 
                            grade = get_custom_grade(pct)
                            t_hy+=h; t_ann+=a; t_grand+=row_tot
                            marks_html += f"<tr><td style='text-align: left; padding-left: 10px;'>{subj}</td><td>{h}</td><td>{a}</td><td>{row_tot}</td><td>{grade}</td></tr>"
                    
                    if display_cls in ["5", "8"]:
                        table_header = f"""<tr><th style="text-align: left; padding-left: 10px;">SUBJECT</th><th>UNIT TEST I<br>[15]</th><th>HALF YEARLY<br>EXAM [35]</th><th>UNIT TEST II<br>[15]</th><th>ANNUAL<br>EXAM [35]</th><th>GRAND TOTAL<br>[100]</th><th>GRADE</th></tr>"""
                        table_footer = f"""<tr style="background-color: #f9f9f9;"><td style="text-align: left; padding-left: 10px;">TOTAL</td><td>{t_ut1}</td><td>{t_hy}</td><td>{t_ut2}</td><td>{t_ann}</td><td>{t_grand}</td><td></td></tr>"""
                        percentage = (t_grand / (len(ordered_subjects) * 100)) * 100 if len(ordered_subjects) > 0 else 0
                    
                    elif display_cls in ["6", "7"]:
                        table_header = f"""<tr><th rowspan="2" style="text-align: left; padding-left: 10px; vertical-align: middle;">SUBJECT</th><th colspan="2">Half yearly exam</th><th colspan="2">Annual exam</th><th colspan="2">TOTAL</th><th rowspan="2" style="vertical-align: middle;">GRADE</th></tr><tr><th style="font-size: 10px;">Obtain</th><th style="font-size: 10px;">Max</th><th style="font-size: 10px;">Obtain</th><th style="font-size: 10px;">Max</th><th style="font-size: 10px;">Obtain</th><th style="font-size: 10px;">Max</th></tr>"""
                        table_footer = f"""<tr style="background-color: #f9f9f9;"><td style="text-align: left; padding-left: 10px;">TOTAL</td><td>{t_hy_obt}</td><td>{t_hy_max}</td><td>{t_ann_obt}</td><td>{t_ann_max}</td><td colspan="3" style="border: none; background: #fff;"></td></tr><tr style="background-color: #f9f9f9;"><td colspan="5" style="text-align: right; padding-right: 15px;">GRAND TOTAL</td><td>{t_grand_obt}</td><td>{t_grand_max}</td><td></td></tr>"""
                        percentage = (t_grand_obt / t_grand_max) * 100 if t_grand_max > 0 else 0
                    
                    else:
                        table_header = f"""<tr><th style="text-align: left; padding-left: 10px;">SUBJECT</th><th>HALF YEARLY<br>EXAM (50)</th><th>ANNUAL<br>EXAM (50)</th><th>GRAND TOTAL<br>[100]</th><th>GRADE</th></tr>"""
                        table_footer = f"""<tr style="background-color: #f9f9f9;"><td style="text-align: left; padding-left: 10px;">TOTAL</td><td>{t_hy}</td><td>{t_ann}</td><td>{t_grand}</td><td></td></tr>"""
                        percentage = (t_grand / (len(ordered_subjects) * 100)) * 100 if len(ordered_subjects) > 0 else 0
                        
                    final_result = "PASSED" if percentage >= 33 else "FAILED"
                    logo_tag = f'<img src="{LOGO_BASE64}" class="logo-img">' if LOGO_BASE64 else ''
                    
                    all_reports_html += f"""
                    <div class="main-box">
                        <div class="header-box">
                            <div class="reg-no">REG-1778</div>
                            {logo_tag}
                            <h1 class="school-name">M.S. PUBLIC SCHOOL</h1>
                            <h3 class="school-address">LARAWAK KACHHAWA MIRZAPUR - 231501</h3>
                            <h3 class="session-text">SESSION (2025-26)</h3>
                        </div>
                        <hr style="border: 1px solid black; margin-top: 15px; margin-bottom: 20px;">
                        <div class="title-div"><span>PROGRESS REPORT CARD</span></div>
                        {info_table_html}
                        <table class="marks-table">{table_header}{marks_html}{table_footer}</table>
                        <table class="footer-table">
                            <tr><td style="width: 40%;">RESULT</td><td>{final_result}</td></tr>
                            <tr><td>PERCENTAGE</td><td>{percentage:.2f}%</td></tr>
                            <tr><td>CHARACTER</td><td>GOOD</td></tr>
                            <tr><td>DATE OF ISSUE</td><td>30-03-2026</td></tr>
                        </table>
                        <div class="sign-container">
                            <div>SIGNATURE OF CLASS TEACHER</div>
                            <div style="text-align: right;">HEADMASTER<br>SIGNATURE & SEAL</div>
                        </div>
                    </div>
                    """
                
                final_html = f"""<html><head><style>body {{ font-family: 'Arial', sans-serif; font-size: 13px; color: black; background: #fff; margin: 0; padding: 0; }} .main-box {{ width: 210mm; min-height: 297mm; margin: 0 auto; padding: 30px 40px; box-sizing: border-box; text-transform: uppercase; position: relative; z-index: 1; page-break-after: always; }} .header-box {{ position: relative; text-align: center; margin-bottom: 5px; }} .reg-no {{ position: absolute; top: 0; right: 0; font-size: 14px; font-weight: bold; color: #000; }} .logo-img {{ position: absolute; top: 0; left: 0; width: 110px; }} .school-name {{ color: #FF0000; margin: 0; font-size: 36px; font-weight: bold; letter-spacing: 1px; padding-top: 15px; font-family: 'Times New Roman', serif; }} .school-address {{ margin: 5px 0 2px 0; font-size: 14px; font-weight: bold; color: #000; }} .session-text {{ margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #000; }} .title-div {{ text-align: center; margin: 20px 0; }} .title-div span {{ color: #0000FF; font-size: 22px; text-decoration: underline; font-weight: bold; }} .info-table {{ width: 100%; border: none; font-weight: bold; font-size: 13px; margin-bottom: 25px; border-collapse: collapse; }} .info-table td {{ padding: 6px 0; border: none; }} .marks-table {{ width: 100%; border-collapse: collapse; text-align: center; font-weight: bold; margin-bottom: 30px; font-size: 12px; }} .marks-table th, .marks-table td {{ border: 1px solid #000; padding: 8px 5px; }} .marks-table th {{ background-color: #fff; font-size: 11px; }} .footer-table {{ width: 45%; font-weight: bold; margin-bottom: 60px; border-collapse: collapse; font-size: 12px; }} .footer-table td {{ border: 1px solid #000; padding: 6px 10px; }} .sign-container {{ display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; margin-top: 60px; }} @media print {{ @page {{ size: A4 portrait; margin: 5mm; }} body {{ padding: 0; -webkit-print-color-adjust: exact !important; }} .main-box {{ width: 100%; min-height: auto; padding: 15px 20px; }} }}</style></head><body onload="setTimeout(() => window.print(), 500)">{all_reports_html}</body></html>"""
                components.html(final_html, height=1100, scrolling=True)
                st.write("---"); st.stop()

        tab1, tab2 = st.tabs(["👤 Print Single Report Card", "🏫 Print Entire Class (Batch)"])
        
        with tab1:
            r_roll_in = st.number_input("Enter Roll No to Print Report Card", min_value=1, step=1)
            if st.button("Generate Single Report Card"):
                c.execute("SELECT name FROM student_master WHERE roll_no=?", (r_roll_in,))
                if c.fetchone(): 
                    st.session_state.report_preview = {"mode": "SINGLE", "val1": r_roll_in, "fields": sel_fields}
                    force_rerun()
                else: st.error("Roll No not found!")
                
        with tab2:
            r_cls = st.selectbox("Select Class to Print All Reports", c_list, key="batch_report_cls")
            if st.button("Generate Class Report Cards"):
                c.execute("SELECT COUNT(*) FROM student_master WHERE class LIKE ?", (f"{r_cls}%",))
                if c.fetchone()[0] > 0: 
                    st.session_state.report_preview = {"mode": "BATCH", "val1": r_cls, "fields": sel_fields}
                    force_rerun()
                else: st.error("No students found in this class!")