import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from database import conn, c, c_list  # ✅ यहाँ से exam_list हटा दिया गया है
from helpers import *

def show_exam_management():
    if 'admit_preview' not in st.session_state: st.session_state.admit_preview = None
    if 'report_preview' not in st.session_state: st.session_state.report_preview = None

    exam_menu = st.sidebar.radio("Exam Menu", ["🎯 Exam Dashboard", "📅 Setup Admit Card", "📝 Bulk Marks Entry", "🖨️ Print Admit Card", "📄 Print Report Card"])
    
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
    # 2. SETUP ADMIT CARD TIMETABLE
    # ==========================================
    elif exam_menu == "📅 Setup Admit Card":
        st.subheader("Set Class-wise Admit Card Timetable")
        colA, colB, colC = st.columns(3)
        tt_cls = colA.selectbox("Select Class", c_list)
        tt_exam = colB.selectbox("Select Exam", exam_list)
        tt_time = colC.text_input("Time Slot", value="10:30 AM - 01:30 PM")
        
        st.write("---")
        st.markdown("### 📝 Enter Dates & Subjects")
        
        c.execute("SELECT * FROM admit_timetable WHERE class=? AND exam_name=?", (tt_cls, tt_exam))
        ext = c.fetchone()
        
        d_vals = [datetime.today().date()] * 10
        s_vals = ["---"] * 10
        if ext:
            for i in range(10):
                try: d_vals[i] = datetime.strptime(ext[3 + i*2], "%Y-%m-%d").date()
                except: pass
                if ext[4 + i*2]: s_vals[i] = ext[4 + i*2]
        
        base_subs = ["---"] + get_subjects_for_class(tt_cls)
        for extra in ["ORAL", "ART & ORAL", "MORAL EDU & PHYSICAL", "AGRICULTURE & PHYSICAL", "MATH/H.SCIENCE"]:
            if extra not in base_subs: base_subs.append(extra)
            
        selected_subs = []
        def get_opts(curr_val): return [x for x in base_subs if x not in selected_subs or x == curr_val]
        def get_idx(val, opts): return opts.index(val) if val in opts else 0

        c1, c2, c3, c4 = st.columns(4)
        d1 = c1.date_input("Date 1", value=d_vals[0])
        opts1 = get_opts(s_vals[0]); s1 = c2.selectbox("Sub 1", opts1, index=get_idx(s_vals[0], opts1))
        if s1 != "---": selected_subs.append(s1)
        
        d6 = c3.date_input("Date 6", value=d_vals[5])
        opts6 = get_opts(s_vals[5]); s6 = c4.selectbox("Sub 6", opts6, index=get_idx(s_vals[5], opts6))
        if s6 != "---": selected_subs.append(s6)
        
        d2 = c1.date_input("Date 2", value=d_vals[1])
        opts2 = get_opts(s_vals[1]); s2 = c2.selectbox("Sub 2", opts2, index=get_idx(s_vals[1], opts2))
        if s2 != "---": selected_subs.append(s2)
        
        d7 = c3.date_input("Date 7", value=d_vals[6])
        opts7 = get_opts(s_vals[6]); s7 = c4.selectbox("Sub 7", opts7, index=get_idx(s_vals[6], opts7))
        if s7 != "---": selected_subs.append(s7)
        
        d3 = c1.date_input("Date 3", value=d_vals[2])
        opts3 = get_opts(s_vals[2]); s3 = c2.selectbox("Sub 3", opts3, index=get_idx(s_vals[2], opts3))
        if s3 != "---": selected_subs.append(s3)
        
        d8 = c3.date_input("Date 8", value=d_vals[7])
        opts8 = get_opts(s_vals[7]); s8 = c4.selectbox("Sub 8", opts8, index=get_idx(s_vals[7], opts8))
        if s8 != "---": selected_subs.append(s8)
        
        d4 = c1.date_input("Date 4", value=d_vals[3])
        opts4 = get_opts(s_vals[3]); s4 = c2.selectbox("Sub 4", opts4, index=get_idx(s_vals[3], opts4))
        if s4 != "---": selected_subs.append(s4)
        
        d9 = c3.date_input("Date 9", value=d_vals[8])
        opts9 = get_opts(s_vals[8]); s9 = c4.selectbox("Sub 9", opts9, index=get_idx(s_vals[8], opts9))
        if s9 != "---": selected_subs.append(s9)
        
        d5 = c1.date_input("Date 5", value=d_vals[4])
        opts5 = get_opts(s_vals[4]); s5 = c2.selectbox("Sub 5", opts5, index=get_idx(s_vals[4], opts5))
        if s5 != "---": selected_subs.append(s5)
        
        d10 = c3.date_input("Date 10", value=d_vals[9])
        opts10 = get_opts(s_vals[9]); s10 = c4.selectbox("Sub 10", opts10, index=get_idx(s_vals[9], opts10))
        if s10 != "---": selected_subs.append(s10)

        if st.button("💾 Save Timetable for this Class"):
            c.execute("DELETE FROM admit_timetable WHERE class=? AND exam_name=?", (tt_cls, tt_exam))
            c.execute("INSERT INTO admit_timetable VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
                      (tt_cls, tt_exam, tt_time, str(d1), s1, str(d2), s2, str(d3), s3, str(d4), s4, str(d5), s5, str(d6), s6, str(d7), s7, str(d8), s8, str(d9), s9, str(d10), s10))
            conn.commit(); st.success(f"✅ Timetable Saved for Class {tt_cls}!")

    # ==========================================
    # 3. BULK MARKS ENTRY
    # ==========================================
    elif exam_menu == "📝 Bulk Marks Entry":
        st.subheader("✏️ Batch Marks Entry (Excel Style)")
        col1, col2 = st.columns(2)
        m_cls = col1.selectbox("Select Class", c_list)
        cls_subjects = get_subjects_for_class(m_cls)
        m_sub = col2.selectbox("Select Subject", cls_subjects)

        c.execute("SELECT roll_no, name FROM student_master WHERE class=? ORDER BY roll_no", (m_cls,))
        students = c.fetchall()

        if students:
            data = []
            for roll, name in students:
                c.execute("SELECT ut1, hy, ut2, annual FROM marks_entry WHERE roll_no=? AND subject=?", (roll, m_sub))
                existing = c.fetchone()
                if existing: data.append({"Roll No": roll, "Student Name": name.upper(), "UT1 (15)": existing[0], "HY (35)": existing[1], "UT2 (15)": existing[2], "Annual (35)": existing[3]})
                else: data.append({"Roll No": roll, "Student Name": name.upper(), "UT1 (15)": 0, "HY (35)": 0, "UT2 (15)": 0, "Annual (35)": 0})

            df_marks = pd.DataFrame(data)
            edited_df = st.data_editor(df_marks, disabled=["Roll No", "Student Name"], hide_index=True, use_container_width=True,
                column_config={"UT1 (15)": st.column_config.NumberColumn(min_value=0, max_value=15), "HY (35)": st.column_config.NumberColumn(min_value=0, max_value=35), "UT2 (15)": st.column_config.NumberColumn(min_value=0, max_value=15), "Annual (35)": st.column_config.NumberColumn(min_value=0, max_value=35)})

            if st.button(f"💾 Save All Marks for {m_sub}"):
                for index, row in edited_df.iterrows():
                    r_no, ut1, hy, ut2, ann = row["Roll No"], row["UT1 (15)"], row["HY (35)"], row["UT2 (15)"], row["Annual (35)"]
                    c.execute("SELECT id FROM marks_entry WHERE roll_no=? AND subject=?", (r_no, m_sub))
                    if c.fetchone(): c.execute("UPDATE marks_entry SET ut1=?, hy=?, ut2=?, annual=? WHERE roll_no=? AND subject=?", (ut1, hy, ut2, ann, r_no, m_sub))
                    else: c.execute("INSERT INTO marks_entry (roll_no, subject, ut1, hy, ut2, annual) VALUES (?, ?, ?, ?, ?, ?)", (r_no, m_sub, ut1, hy, ut2, ann))
                conn.commit(); st.success("✅ Marks saved!"); force_rerun()
        else: st.warning("⚠️ No students found in this class.")

    # ==========================================
    # 4. PRINT ADMIT CARD
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
                c.execute("SELECT roll_no, name, class, father_name FROM student_master WHERE roll_no=?", (val1,))
                stu = c.fetchone()
                if stu: students_to_print.append(stu)
            else:
                c.execute("SELECT roll_no, name, class, father_name FROM student_master WHERE class=? ORDER BY roll_no", (val1,))
                students_to_print = c.fetchall()

            if not students_to_print: st.error("No students found!")
            else:
                target_cls = students_to_print[0][2]
                c.execute("SELECT * FROM admit_timetable WHERE class=? AND exam_name=?", (target_cls, exam_sel))
                tt = c.fetchone()
                if not tt: tt = [target_cls, exam_sel, "10:30 AM - 01:30 PM", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---", "", "---"]

                all_cards_html = ""
                for stu_item in students_to_print:
                    r_num, s_name, s_class, f_name = stu_item
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
                                <td class="lbl">CLASS :</td><td class="val">{s_class}</td>
                                <td colspan="2" style="text-align: right; vertical-align: bottom;">
                                    <div style="border-top: 1.5px solid #000; padding-top: 2px; font-size: 11px; color: #000; font-weight: bold; width: 160px; float: right; text-align: center;">PRINCIPAL'S SIGNATURE</div>
                                </td>
                            </tr>
                        </table>
                        <div class="time-lbl">TIME - ({tt[2]})</div>
                        <table class="tt-table">
                            <tr style="background-color: #E6F0FA;"><th>DAY</th><th>SUBJECT</th><th>DAY</th><th>SUBJECT</th></tr>
                            <tr><td>{fd(tt[3], tt[4])}</td><td>{fs(tt[4])}</td><td>{fd(tt[13], tt[14])}</td><td>{fs(tt[14])}</td></tr>
                            <tr><td>{fd(tt[5], tt[6])}</td><td>{fs(tt[6])}</td><td>{fd(tt[15], tt[16])}</td><td>{fs(tt[16])}</td></tr>
                            <tr><td>{fd(tt[7], tt[8])}</td><td>{fs(tt[8])}</td><td>{fd(tt[17], tt[18])}</td><td>{fs(tt[18])}</td></tr>
                            <tr><td>{fd(tt[9], tt[10])}</td><td>{fs(tt[10])}</td><td>{fd(tt[19], tt[20])}</td><td>{fs(tt[20])}</td></tr>
                            <tr><td>{fd(tt[11], tt[12])}</td><td>{fs(tt[12])}</td><td>{fd(tt[21], tt[22])}</td><td>{fs(tt[22])}</td></tr>
                        </table>
                    </div>
                    """

                final_html = f"""
                <html><head><style>
                    body {{ font-family: 'Calibri', Arial, sans-serif; font-size: 11px; margin: 0; padding: 0; background: #fff; }}
                    .card-container {{ width: 140mm; height: 94mm; margin: 10px auto; border: 2px solid #1F497D; padding: 8px 14px; position: relative; box-sizing: border-box; background: white; overflow: hidden; }}
                    .header-table {{ width: 100%; border-collapse: collapse; text-align: center; margin-bottom: 6px; }}
                    .header-table h1 {{ color: #FF0000; margin: 0; font-size: 23px; font-family: 'Times New Roman', serif; }}
                    .header-table h3 {{ color: #000; margin: 2px 0; font-size: 13px; text-transform: uppercase; }}
                    .header-table h4 {{ color: #0000FF; margin: 0; text-decoration: underline; font-size: 13px; }}
                    .info-table {{ width: 100%; border-collapse: collapse; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; }}
                    .info-table td {{ padding: 2px 0; }}
                    .lbl {{ color: #000; width: 22%; }} .val {{ color: #0000FF; width: 48%; }}
                    .time-lbl {{ color: #FF0000; font-weight: bold; font-size: 12px; margin-bottom: 2px; }}
                    .tt-table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 11px; }}
                    .tt-table th, .tt-table td {{ border: 1px solid #1F497D; padding: 4px; font-weight: bold; }}
                    @media print {{ 
                        @page {{ size: 148mm 100mm landscape; margin: 2mm; }} 
                        body {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }} 
                        .card-container {{ width: 100%; height: 96mm; margin: 0; border: 2px solid #1F497D; page-break-after: always; }}
                    }}
                </style></head><body onload="setTimeout(() => window.print(), 500)">
                    {all_cards_html}
                </body></html>
                """
                
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
                c.execute("SELECT COUNT(*) FROM student_master WHERE class=?", (b_cls,))
                if c.fetchone()[0] > 0: st.session_state.admit_preview = ("BATCH", b_cls, b_exam); force_rerun()
                else: st.error("No students found in this class!")

    # ==========================================
    # 5. PRINT REPORT CARD (FIXED A4 LAYOUT - NO BACKGROUND, SINGLE LINE)
    # ==========================================
    elif exam_menu == "📄 Print Report Card":
        st.subheader("Generate Full A4 Report Card (Official School Design)")
        
        if st.session_state.report_preview:
            r_roll = st.session_state.report_preview
            st.markdown("### 🖨️ A4 Report Card Print View")
            if st.button("❌ Close Preview & Go Back"):
                st.session_state.report_preview = None; force_rerun()
                
            c.execute("SELECT name, class, father_name, mother_name, dob, sch_no FROM student_master WHERE roll_no=?", (r_roll,))
            stu = c.fetchone()
            if stu:
                s_name, s_class, f_name, m_name, s_dob, s_sch = stu
                ordered_subjects = get_subjects_for_class(s_class)
                marks_html = ""
                t_ut1 = t_hy = t_ut2 = t_ann = t_grand = 0
                
                for subj in ordered_subjects:
                    c.execute("SELECT ut1, hy, ut2, annual FROM marks_entry WHERE roll_no=? AND subject=?", (r_roll, subj))
                    res = c.fetchone()
                    u1, h, u2, a = res if res else (0, 0, 0, 0)
                    row_tot = u1 + h + u2 + a
                    grade = get_grade(row_tot)
                    t_ut1+=u1; t_hy+=h; t_ut2+=u2; t_ann+=a; t_grand+=row_tot
                    marks_html += f"<tr><td style='text-align: left; padding-left: 10px;'>{subj}</td><td>{u1}</td><td>{h}</td><td>{u2}</td><td>{a}</td><td>{row_tot}</td><td>{grade}</td></tr>"
                
                percentage = (t_grand / (len(ordered_subjects)*100)) * 100 if len(ordered_subjects) > 0 else 0
                final_result = "PASSED" if percentage >= 33 else "FAILED"
                logo_tag = f'<img src="{LOGO_BASE64}" class="logo-img">' if LOGO_BASE64 else ''
                
                report_html = f"""
                <html><head><style>
                    body {{ font-family: 'Arial', sans-serif; font-size: 13px; color: black; background: #fff; margin: 0; padding: 0; }}
                    .main-box {{ width: 210mm; min-height: 297mm; margin: 0 auto; padding: 30px 40px; box-sizing: border-box; text-transform: uppercase; position: relative; z-index: 1; }}
                    
                    .header-box {{ position: relative; text-align: center; margin-bottom: 5px; }}
                    .reg-no {{ position: absolute; top: 0; right: 0; font-size: 14px; font-weight: bold; color: #000; }}
                    .logo-img {{ position: absolute; top: 0; left: 0; width: 110px; }}
                    .school-name {{ color: #FF0000; margin: 0; font-size: 36px; font-weight: bold; letter-spacing: 1px; padding-top: 15px; font-family: 'Times New Roman', serif; }}
                    .school-address {{ margin: 5px 0 2px 0; font-size: 14px; font-weight: bold; color: #000; }}
                    .session-text {{ margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #000; }}
                    
                    .title-div {{ text-align: center; margin: 20px 0; }}
                    .title-div span {{ color: #0000FF; font-size: 22px; text-decoration: underline; font-weight: bold; }}
                    
                    .info-table {{ width: 100%; border: none; font-weight: bold; font-size: 13px; margin-bottom: 25px; border-collapse: collapse; }}
                    .info-table td {{ padding: 6px 0; border: none; }}
                    
                    .marks-table {{ width: 100%; border-collapse: collapse; text-align: center; font-weight: bold; margin-bottom: 30px; font-size: 12px; }}
                    .marks-table th, .marks-table td {{ border: 1px solid #000; padding: 8px 5px; }}
                    .marks-table th {{ background-color: #fff; font-size: 11px; }}
                    
                    .footer-table {{ width: 45%; font-weight: bold; margin-bottom: 60px; border-collapse: collapse; font-size: 12px; }}
                    .footer-table td {{ border: 1px solid #000; padding: 6px 10px; }}
                    
                    .sign-container {{ display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; margin-top: 60px; }}
                    
                    @media print {{ 
                        @page {{ size: A4 portrait; margin: 5mm; }} 
                        body {{ padding: 0; -webkit-print-color-adjust: exact !important; }} 
                        .main-box {{ width: 100%; min-height: auto; padding: 15px 20px; }} 
                    }}
                </style></head><body onload="setTimeout(() => window.print(), 500)">
                    <div class="main-box">
                        <div class="header-box">
                            <div class="reg-no">REG-1778</div>
                            {logo_tag}
                            <h1 class="school-name">M.S. PUBLIC SCHOOL</h1>
                            <h3 class="school-address">LARAWAK KACHHAWA MIRZAPUR - 231501</h3>
                            <h3 class="session-text">SESSION (2025-26)</h3>
                        </div>
                        
                        <!-- CLEAN SINGLE LINE WITH TOP MARGIN -->
                        <hr style="border: 1px solid black; margin-top: 15px; margin-bottom: 20px;">
                        
                        <div class="title-div">
                            <span>PROGRESS REPORT CARD</span>
                        </div>
                        
                        <table class="info-table">
                            <tr>
                                <td style="width: 15%;">NAME</td><td style="width: 45%;">: {s_name}</td>
                                <td style="width: 15%;">CLASS</td><td style="width: 25%;">: {s_class}</td>
                            </tr>
                            <tr>
                                <td>FATHER'S NAME</td><td>: {f_name}</td>
                                <td>ROLL NO</td><td>: {r_roll}</td>
                            </tr>
                            <tr>
                                <td>MOTHER'S NAME</td><td>: {m_name}</td>
                                <td>SCH NO</td><td>: {s_sch}</td>
                            </tr>
                            <tr>
                                <td></td><td></td>
                                <td>DOB</td><td>: {s_dob}</td>
                            </tr>
                        </table>
                        
                        <table class="marks-table">
                            <tr>
                                <th style="text-align: left; padding-left: 10px;">SUBJECT</th>
                                <th>UNIT TEST I<br>[15]</th>
                                <th>HALF YEARLY<br>EXAM [35]</th>
                                <th>UNIT TEST II<br>[15]</th>
                                <th>ANNUAL<br>EXAM [35]</th>
                                <th>GRAND TOTAL<br>[100]</th>
                                <th>GRADE</th>
                            </tr>
                            {marks_html}
                            <tr style="background-color: #f9f9f9;">
                                <td style="text-align: left; padding-left: 10px;">TOTAL</td>
                                <td>{t_ut1}</td><td>{t_hy}</td><td>{t_ut2}</td><td>{t_ann}</td><td>{t_grand}</td><td></td>
                            </tr>
                        </table>
                        
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
                </body></html>
                """
                
                components.html(report_html, height=1100, scrolling=True)
                st.write("---"); st.stop()
            else:
                st.error("Student Not Found!")

        r_roll_in = st.number_input("Enter Roll No to Print Report Card", min_value=1, step=1)
        if st.button("Generate Report Card"):
            c.execute("SELECT name FROM student_master WHERE roll_no=?", (r_roll_in,))
            if c.fetchone(): st.session_state.report_preview = r_roll_in; force_rerun()
            else: st.error("Roll No not found!")